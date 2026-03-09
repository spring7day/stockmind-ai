"""
StockMind AI — 주식 관련 API 라우터
GET /api/stocks/popular              — 인기 종목 목록 (BUG-001)
GET /api/stocks/search               — 종목 검색
GET /api/stocks/{ticker}             — 종목 상세 정보
GET /api/stocks/{ticker}/price       — 종목 현재 가격 (BUG-002: camelCase 필드명)
GET /api/stocks/{ticker}/chart       — 종목 차트 데이터 (OHLCV)
GET /api/stocks/{ticker}/analysis    — AI 심층 분석 (전체)
GET /api/stocks/{ticker}/analysis/{tab} — 탭별 AI 분석 (BUG-003)
GET /api/stocks/{ticker}/news        — 뉴스/공시
GET /api/stocks/{ticker}/signals     — 숨겨진 인사이트 신호

신규 엔드포인트는 ApiResponse{success, data} 래퍼로 응답합니다 (BUG-011).
기존 호환성 엔드포인트 (/{ticker}, /{ticker}/analysis)는 래퍼 없이 직접 반환합니다.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.config import settings
from app.models.response import ApiResponse
from app.models.stock import (
    AnalysisResult,
    NewsResponse,
    SearchResponse,
    StockInfo,
    StockPriceResponse,
    StockSummaryResponse,
    TabAnalysisResult,
)
from app.services import ai_analyzer, data_collector
from app.services.cache import (
    cache_key_analysis,
    cache_key_news,
    cache_key_search,
    cache_key_signals,
    cache_key_stock_info,
    cache_service,
)
from app.utils.helpers import is_valid_ticker, normalize_ticker

logger = logging.getLogger(__name__)

router = APIRouter()

# 인기 종목 코드 목록
POPULAR_TICKERS = [
    "005930",  # 삼성전자
    "000660",  # SK하이닉스
    "035420",  # NAVER
    "005380",  # 현대차
    "051910",  # LG화학
    "035720",  # 카카오
]

# ────────────────────────────────────────────────
# 탭 → 분석 결과 변환 헬퍼 (BUG-003)
# ────────────────────────────────────────────────

DISCLAIMER = (
    "본 분석은 AI가 생성한 참고 정보이며, 투자 권유가 아닙니다. "
    "투자 결정은 본인의 판단과 책임 하에 이루어져야 합니다. "
    "과거 성과가 미래 수익을 보장하지 않습니다."
)


def _map_analysis_to_tab(result: AnalysisResult, tab: str) -> TabAnalysisResult:
    """AnalysisResult 전체 결과를 탭별 TabAnalysisResult로 변환합니다."""
    tab_map = {
        "technical": _build_technical_tab,
        "fundamental": _build_fundamental_tab,
        "insights": _build_insights_tab,
        "sentiment": _build_sentiment_tab,
    }
    builder = tab_map.get(tab)
    if builder is None:
        raise ValueError(f"지원하지 않는 탭: {tab}. 허용값: technical|fundamental|insights|sentiment")
    return builder(result, tab)


def _build_technical_tab(result: AnalysisResult, tab: str) -> TabAnalysisResult:
    t = result.technical
    details_parts = [
        "## 기술적 분석\n",
        f"**추세:** {t.trend}",
        f"**거래량 추세:** {t.volume_trend}",
    ]
    if t.rsi is not None:
        details_parts.append(f"**RSI:** {t.rsi:.1f}")
    if t.support_levels:
        details_parts.append(f"**지지선:** {', '.join(f'{p:,.0f}원' for p in t.support_levels)}")
    if t.resistance_levels:
        details_parts.append(f"**저항선:** {', '.join(f'{p:,.0f}원' for p in t.resistance_levels)}")
    details_parts.append(f"\n### AI 요약\n{t.summary}")
    if t.signals:
        details_parts.append("\n### 주요 신호\n" + "\n".join(f"- {s}" for s in t.signals))
    details_parts.append(f"\n> {result.disclaimer}")

    return TabAnalysisResult(
        tab=tab,
        ticker=result.ticker,
        summary=t.summary,
        details="\n".join(filter(None, details_parts)),
        generatedAt=result.analyzed_at.isoformat() + "Z",
        disclaimer=result.disclaimer,
    )


def _build_fundamental_tab(result: AnalysisResult, tab: str) -> TabAnalysisResult:
    f = result.fundamental
    details_parts = [
        "## 펀더멘털 분석\n",
        f"**밸류에이션:** {f.valuation}",
        f"**성장 가능성:** {f.growth_potential}",
        f"**재무 건전성:** {f.financial_health}",
        f"**동종업계 비교:** {f.peer_comparison}",
        f"\n### AI 요약\n{f.summary}",
    ]
    if f.risks:
        details_parts.append("\n### 리스크 요소\n" + "\n".join(f"- {r}" for r in f.risks))
    if f.opportunities:
        details_parts.append("\n### 기회 요소\n" + "\n".join(f"- {o}" for o in f.opportunities))
    details_parts.append(f"\n> {result.disclaimer}")

    return TabAnalysisResult(
        tab=tab,
        ticker=result.ticker,
        summary=f.summary,
        details="\n".join(filter(None, details_parts)),
        generatedAt=result.analyzed_at.isoformat() + "Z",
        disclaimer=result.disclaimer,
    )


def _build_insights_tab(result: AnalysisResult, tab: str) -> TabAnalysisResult:
    h = result.hidden_insights
    details_parts = [
        "## 숨겨진 인사이트\n",
        f"**스마트 머니 흐름:** {h.smart_money_flow}",
        f"**기관/외국인 시그널:** {h.dark_pool_signals}",
    ]
    if h.seasonal_patterns:
        details_parts.append(f"**계절적 패턴:** {h.seasonal_patterns}")
    if h.unusual_activity:
        details_parts.append("\n### 이상 징후\n" + "\n".join(f"- {a}" for a in h.unusual_activity))
    if h.catalyst_events:
        details_parts.append("\n### 예상 촉매 이벤트\n" + "\n".join(f"- {e}" for e in h.catalyst_events))
    details_parts.append(f"\n### AI 요약\n{h.summary}")
    details_parts.append(f"\n> {result.disclaimer}")

    return TabAnalysisResult(
        tab=tab,
        ticker=result.ticker,
        summary=h.summary,
        details="\n".join(filter(None, details_parts)),
        generatedAt=result.analyzed_at.isoformat() + "Z",
        disclaimer=result.disclaimer,
    )


def _build_sentiment_tab(result: AnalysisResult, tab: str) -> TabAnalysisResult:
    s = result.sentiment
    details_parts = [
        "## 뉴스 센티먼트 분석\n",
        f"**전반적 심리:** {s.overall_sentiment}",
        f"**뉴스 센티먼트:** {s.news_sentiment}",
        f"**공시 센티먼트:** {s.disclosure_sentiment}",
        f"**개인투자자 관심도:** {s.retail_interest}",
    ]
    if s.social_buzz:
        details_parts.append(f"**소셜 화제도:** {s.social_buzz}")
    details_parts.append(f"\n### AI 요약\n{s.summary}")
    details_parts.append(f"\n> {result.disclaimer}")

    return TabAnalysisResult(
        tab=tab,
        ticker=result.ticker,
        summary=s.summary,
        details="\n".join(filter(None, details_parts)),
        generatedAt=result.analyzed_at.isoformat() + "Z",
        disclaimer=result.disclaimer,
    )


# ────────────────────────────────────────────────
# 엔드포인트
# ────────────────────────────────────────────────

@router.get("/popular", summary="인기 종목 목록")
async def get_popular_stocks() -> ApiResponse[List[StockSummaryResponse]]:
    """
    자주 조회되는 KOSPI/KOSDAQ 대형주 목록을 반환합니다.
    주가 데이터 수집에 실패하면 종목명과 코드만 반환합니다.
    응답: ApiResponse{success, data: StockSummaryResponse[]}
    """
    stock_list = await data_collector.load_stock_list() or {}

    items: List[StockSummaryResponse] = []
    for ticker in POPULAR_TICKERS:
        info = stock_list.get(ticker)
        if info is None:
            continue

        name = info["name"]
        market = info["market"]
        summary = StockSummaryResponse(
            ticker=ticker,
            name=name,
            market=market,
            updatedAt=datetime.utcnow().isoformat() + "Z",
        )

        try:
            price = await data_collector.get_stock_price(ticker)
            if price:
                summary.currentPrice = price.current
                summary.openPrice = price.open
                summary.highPrice = price.high
                summary.lowPrice = price.low
                summary.closePrice = price.prev_close
                summary.change = price.change
                summary.changePercent = price.change_pct
                summary.volume = price.volume
        except Exception:
            pass

        items.append(summary)

    return ApiResponse.ok(items)


@router.get("/search", summary="종목 검색")
async def search_stocks(
    q: str = Query(..., min_length=1, max_length=50, description="종목명 또는 종목코드"),
    limit: int = Query(20, ge=1, le=50, description="반환할 최대 결과 수"),
) -> ApiResponse[SearchResponse]:
    """
    종목명 또는 종목코드로 KOSPI/KOSDAQ 종목을 검색합니다.
    예: q=삼성전자, q=005930
    """
    # 캐시 확인
    cache_key = cache_key_search(q)
    cached = await cache_service.get(cache_key)
    if cached:
        return ApiResponse.ok(SearchResponse(**cached))

    # 종목 목록이 로드되지 않은 경우 로드
    await data_collector.load_stock_list()

    results = data_collector.search_stocks(q, limit=limit)

    response = SearchResponse(
        query=q,
        results=results,
        total=len(results),
    )

    # 검색 결과 캐시 (2분)
    await cache_service.set(cache_key, response.model_dump(), ttl=120)

    return ApiResponse.ok(response)


@router.get("/{ticker}/price", summary="종목 현재 가격 (프론트엔드 camelCase 필드명)")
async def get_stock_price(ticker: str) -> ApiResponse[StockPriceResponse]:
    """
    종목 코드로 현재 주가 정보를 조회합니다.
    응답 필드 (BUG-002 수정): currentPrice, openPrice, highPrice, lowPrice,
    closePrice, change, changePercent, volume, marketCap?, updatedAt
    """
    ticker = normalize_ticker(ticker)
    if not is_valid_ticker(ticker):
        raise HTTPException(status_code=400, detail="유효하지 않은 종목코드입니다. 6자리 숫자를 입력해주세요.")

    # 캐시 확인 (주가는 1분 캐시)
    cache_key = f"stock:{ticker}:price_v2"
    cached = await cache_service.get(cache_key)
    if cached:
        return ApiResponse.ok(StockPriceResponse(**cached))

    stock_list = await data_collector.load_stock_list() or {}

    if ticker not in stock_list:
        raise HTTPException(status_code=404, detail=f"종목 {ticker}을(를) 찾을 수 없습니다.")

    price = await data_collector.get_stock_price(ticker)
    if price is None:
        raise HTTPException(status_code=503, detail=f"종목 {ticker}의 주가 데이터를 가져올 수 없습니다.")

    # 시가총액 조회 (StockInfo에서 가져오기)
    market_cap: Optional[float] = None
    try:
        stock_info = await data_collector.get_full_stock_info(ticker)
        if stock_info and stock_info.fundamentals:
            market_cap = stock_info.fundamentals.market_cap
    except Exception:
        pass

    price_response = StockPriceResponse.from_stock_price(ticker, price, market_cap)
    await cache_service.set(cache_key, price_response.model_dump(), ttl=60)
    return ApiResponse.ok(price_response)


@router.get("/{ticker}/chart", summary="종목 차트 데이터 (OHLCV)")
async def get_stock_chart(
    ticker: str,
    period: str = Query("3M", description="기간: 1D, 1W, 1M, 3M, 1Y"),
):
    """
    종목의 OHLCV 캔들 데이터를 반환합니다.
    period: 1D(1일), 1W(1주), 1M(1개월), 3M(3개월), 1Y(1년)
    차트 데이터는 배열 형태로 직접 반환합니다 (ApiResponse 미적용 — 경량 엔드포인트).
    """
    ticker = normalize_ticker(ticker)
    if not is_valid_ticker(ticker):
        raise HTTPException(status_code=400, detail="유효하지 않은 종목코드입니다.")

    period_days = {"1D": 1, "1W": 7, "1M": 30, "3M": 90, "1Y": 365}.get(period, 90)

    cache_key = f"stock:{ticker}:chart:{period}"
    cached = await cache_service.get(cache_key)
    if cached:
        return cached

    import asyncio
    from pykrx import stock as krx

    def _fetch_ohlcv():
        end = datetime.now()
        start = end - timedelta(days=period_days + 10)  # 주말/공휴일 여유분
        start_str = start.strftime("%Y%m%d")
        end_str = end.strftime("%Y%m%d")
        try:
            df = krx.get_market_ohlcv_by_date(start_str, end_str, ticker)
            if df.empty:
                return []
            candles = []
            for date_idx, row in df.iterrows():
                date_str = date_idx.strftime("%Y-%m-%d") if hasattr(date_idx, "strftime") else str(date_idx)[:10]
                candles.append({
                    "time": date_str,
                    "open": int(row["시가"]),
                    "high": int(row["고가"]),
                    "low": int(row["저가"]),
                    "close": int(row["종가"]),
                    "volume": int(row["거래량"]),
                })
            return candles
        except Exception as e:
            logger.error(f"[{ticker}] 차트 데이터 수집 실패: {e}")
            return []

    loop = asyncio.get_running_loop()
    candles = await loop.run_in_executor(None, _fetch_ohlcv)

    if not candles:
        raise HTTPException(status_code=503, detail=f"종목 {ticker}의 차트 데이터를 가져올 수 없습니다.")

    await cache_service.set(cache_key, candles, ttl=300)
    return candles


@router.get("/{ticker}", response_model=StockInfo, summary="종목 상세 정보")
async def get_stock_info(ticker: str):
    """
    종목 코드로 주가, 펀더멘털, 투자자 동향, 공매도 정보를 조회합니다.
    종목코드 예: 005930 (삼성전자), 000660 (SK하이닉스)
    이 엔드포인트는 기존 호환성을 위해 StockInfo를 직접 반환합니다.
    """
    ticker = normalize_ticker(ticker)
    if not is_valid_ticker(ticker):
        raise HTTPException(status_code=400, detail="유효하지 않은 종목코드입니다. 6자리 숫자를 입력해주세요.")

    # 캐시 확인
    cache_key = cache_key_stock_info(ticker)
    cached = await cache_service.get(cache_key)
    if cached:
        return StockInfo(**cached)

    stock_info = await data_collector.get_full_stock_info(ticker)
    if stock_info is None:
        raise HTTPException(status_code=404, detail=f"종목 {ticker}을(를) 찾을 수 없습니다.")

    # 캐시 저장 (5분)
    await cache_service.set(cache_key, stock_info.model_dump(), ttl=settings.CACHE_TTL_STOCK_INFO)

    return stock_info


@router.get("/{ticker}/analysis", response_model=AnalysisResult, summary="AI 심층 분석 (전체)")
async def get_stock_analysis(ticker: str):
    """
    Claude AI를 사용한 4가지 심층 분석을 제공합니다:
    - 기술적 분석 (추세, 지지/저항선, RSI)
    - 펀더멘털 분석 (밸류에이션, 성장성, 재무 건전성)
    - 숨겨진 인사이트 (스마트 머니, 이상 징후)
    - 센티먼트 분석 (뉴스, 공시, 투자자 심리)

    전체 분석 결과를 반환합니다. 탭별 결과는 /analysis/{tab} 사용.
    ⚠️ 본 분석은 AI 참고 정보이며 투자 권유가 아닙니다.
    """
    ticker = normalize_ticker(ticker)
    if not is_valid_ticker(ticker):
        raise HTTPException(status_code=400, detail="유효하지 않은 종목코드입니다.")

    # 캐시 확인 (AI 분석은 1시간 캐시)
    cache_key = cache_key_analysis(ticker)
    cached = await cache_service.get(cache_key)
    if cached:
        result = AnalysisResult(**cached)
        result.cached = True
        return result

    # 주식 정보 수집
    stock_info = await data_collector.get_full_stock_info(ticker)
    if stock_info is None:
        raise HTTPException(status_code=404, detail=f"종목 {ticker}을(를) 찾을 수 없습니다.")

    # 뉴스/공시 수집 (분석 컨텍스트로 활용)
    news_items = []
    try:
        dart_items = await data_collector.get_dart_disclosures(ticker, limit=5)
        naver_items = await data_collector.get_stock_news(ticker, stock_info.name)
        news_items = dart_items + naver_items
    except Exception as e:
        logger.warning(f"[{ticker}] 뉴스 수집 실패 (분석은 계속 진행): {e}")

    # AI 분석 실행
    analysis = await ai_analyzer.run_full_analysis(stock_info, news_items)

    # 캐시 저장 (1시간)
    await cache_service.set(cache_key, analysis.model_dump(), ttl=settings.CACHE_TTL_ANALYSIS)

    return analysis


@router.get("/{ticker}/analysis/{tab}", summary="탭별 AI 분석 결과 (BUG-003)")
async def get_stock_analysis_by_tab(
    ticker: str,
    tab: str,
) -> ApiResponse[TabAnalysisResult]:
    """
    탭별 AI 분석 결과를 반환합니다 (BUG-003 수정).
    tab: technical | fundamental | insights | sentiment

    전체 분석을 수행한 후 해당 탭의 결과만 추출하여 반환합니다.
    응답 구조는 프론트엔드 AnalysisResult 인터페이스와 일치합니다:
    { tab, ticker, summary, score?, details, generatedAt, disclaimer }

    ⚠️ 본 분석은 AI 참고 정보이며 투자 권유가 아닙니다.
    """
    ticker = normalize_ticker(ticker)
    if not is_valid_ticker(ticker):
        raise HTTPException(status_code=400, detail="유효하지 않은 종목코드입니다.")

    valid_tabs = {"technical", "fundamental", "insights", "sentiment"}
    if tab not in valid_tabs:
        raise HTTPException(
            status_code=400,
            detail=f"유효하지 않은 탭: {tab}. 허용값: {', '.join(sorted(valid_tabs))}",
        )

    # 탭별 캐시 키
    tab_cache_key = f"stock:{ticker}:analysis:tab:{tab}"
    cached = await cache_service.get(tab_cache_key)
    if cached:
        return ApiResponse.ok(TabAnalysisResult(**cached))

    # 전체 분석 캐시 확인 (탭 캐시가 없어도 전체 캐시가 있으면 재활용)
    full_cache_key = cache_key_analysis(ticker)
    full_cached = await cache_service.get(full_cache_key)

    if full_cached:
        full_result = AnalysisResult(**full_cached)
        full_result.cached = True
    else:
        # 주식 정보 수집
        stock_info = await data_collector.get_full_stock_info(ticker)
        if stock_info is None:
            raise HTTPException(status_code=404, detail=f"종목 {ticker}을(를) 찾을 수 없습니다.")

        # 뉴스/공시 수집
        news_items = []
        try:
            dart_items = await data_collector.get_dart_disclosures(ticker, limit=5)
            naver_items = await data_collector.get_stock_news(ticker, stock_info.name)
            news_items = dart_items + naver_items
        except Exception as e:
            logger.warning(f"[{ticker}] 뉴스 수집 실패 (분석은 계속 진행): {e}")

        # AI 분석 실행
        full_result = await ai_analyzer.run_full_analysis(stock_info, news_items)

        # 전체 분석 캐시 저장 (1시간)
        await cache_service.set(full_cache_key, full_result.model_dump(), ttl=settings.CACHE_TTL_ANALYSIS)

    # 탭별 변환
    tab_result = _map_analysis_to_tab(full_result, tab)

    # 탭별 캐시 저장 (전체 캐시와 동일 TTL)
    await cache_service.set(tab_cache_key, tab_result.model_dump(), ttl=settings.CACHE_TTL_ANALYSIS)

    return ApiResponse.ok(tab_result)


@router.get("/{ticker}/news", summary="뉴스 및 공시")
async def get_stock_news(
    ticker: str,
    limit: int = Query(15, ge=1, le=30, description="반환할 최대 항목 수"),
) -> ApiResponse[NewsResponse]:
    """
    종목 관련 최신 뉴스와 OpenDART 공시를 조회합니다.
    뉴스: 네이버 금융 / 공시: OpenDART
    NewsItem에 id, publishedAt(camelCase), sentimentScore, isDisclosure 포함 (BUG-004).
    """
    ticker = normalize_ticker(ticker)
    if not is_valid_ticker(ticker):
        raise HTTPException(status_code=400, detail="유효하지 않은 종목코드입니다.")

    # 캐시 확인
    cache_key = cache_key_news(ticker)
    cached = await cache_service.get(cache_key)
    if cached:
        return ApiResponse.ok(NewsResponse(**cached))

    # 종목 정보 확인
    stock_list = await data_collector.load_stock_list()
    if ticker not in stock_list:
        raise HTTPException(status_code=404, detail=f"종목 {ticker}을(를) 찾을 수 없습니다.")

    stock_name = stock_list[ticker]["name"]

    # 뉴스 + 공시 병렬 수집
    import asyncio

    dart_items, naver_items = await asyncio.gather(
        data_collector.get_dart_disclosures(ticker, limit=10),
        data_collector.get_stock_news(ticker, stock_name),
        return_exceptions=True,
    )

    if isinstance(dart_items, Exception):
        dart_items = []
    if isinstance(naver_items, Exception):
        naver_items = []

    # 공시 먼저, 뉴스 뒤에 배치
    all_items = dart_items + naver_items
    all_items = all_items[:limit]

    response = NewsResponse(
        ticker=ticker,
        name=stock_name,
        items=all_items,
    )

    # 캐시 저장 (10분)
    await cache_service.set(cache_key, response.model_dump(), ttl=settings.CACHE_TTL_NEWS)

    return ApiResponse.ok(response)


@router.get("/{ticker}/signals", summary="숨겨진 인사이트 신호")
async def get_stock_signals(ticker: str) -> ApiResponse[dict]:
    """
    기관/외국인 순매수 흐름, 공매도 비율, 이상 거래 신호를 요약하여 반환합니다.
    빠른 조회를 위한 경량 엔드포인트입니다.

    ⚠️ 본 정보는 AI 참고 정보이며 투자 권유가 아닙니다.
    """
    ticker = normalize_ticker(ticker)
    if not is_valid_ticker(ticker):
        raise HTTPException(status_code=400, detail="유효하지 않은 종목코드입니다.")

    # 캐시 확인
    cache_key = cache_key_signals(ticker)
    cached = await cache_service.get(cache_key)
    if cached:
        return ApiResponse.ok(cached)

    # 주식 정보 수집
    stock_info = await data_collector.get_full_stock_info(ticker)
    if stock_info is None:
        raise HTTPException(status_code=404, detail=f"종목 {ticker}을(를) 찾을 수 없습니다.")

    # 신호 계산
    signals = []

    if stock_info.investor_trading:
        it = stock_info.investor_trading
        if it.foreign and it.foreign > 0:
            signals.append({"type": "foreign_buy", "label": "외국인 순매수", "value": it.foreign, "sentiment": "positive"})
        elif it.foreign and it.foreign < 0:
            signals.append({"type": "foreign_sell", "label": "외국인 순매도", "value": it.foreign, "sentiment": "negative"})

        if it.institutional and it.institutional > 0:
            signals.append({"type": "inst_buy", "label": "기관 순매수", "value": it.institutional, "sentiment": "positive"})
        elif it.institutional and it.institutional < 0:
            signals.append({"type": "inst_sell", "label": "기관 순매도", "value": it.institutional, "sentiment": "negative"})

    if stock_info.short_selling and stock_info.short_selling.short_ratio:
        ratio = stock_info.short_selling.short_ratio
        sentiment = "negative" if ratio > 5.0 else "neutral"
        signals.append({"type": "short_ratio", "label": "공매도 비율", "value": ratio, "unit": "%", "sentiment": sentiment})

    response = {
        "ticker": ticker,
        "name": stock_info.name,
        "signals": signals,
        "disclaimer": "본 신호는 AI 참고 정보이며, 투자 권유가 아닙니다.",
    }

    # 캐시 저장 (30분)
    await cache_service.set(cache_key, response, ttl=settings.CACHE_TTL_SIGNALS)

    return ApiResponse.ok(response)
