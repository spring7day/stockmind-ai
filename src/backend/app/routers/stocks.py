"""
StockMind AI — 주식 관련 API 라우터
GET /api/stocks/search  — 종목 검색
GET /api/stocks/{ticker}  — 종목 상세 정보
GET /api/stocks/{ticker}/analysis  — AI 심층 분석
GET /api/stocks/{ticker}/news  — 뉴스/공시
GET /api/stocks/{ticker}/signals  — 숨겨진 인사이트 신호
"""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.config import settings
from app.models.stock import (
    AnalysisResult,
    NewsResponse,
    SearchResponse,
    StockInfo,
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


@router.get("/search", response_model=SearchResponse, summary="종목 검색")
async def search_stocks(
    q: str = Query(..., min_length=1, max_length=50, description="종목명 또는 종목코드"),
    limit: int = Query(20, ge=1, le=50, description="반환할 최대 결과 수"),
):
    """
    종목명 또는 종목코드로 KOSPI/KOSDAQ 종목을 검색합니다.
    예: q=삼성전자, q=005930
    """
    # 캐시 확인
    cache_key = cache_key_search(q)
    cached = await cache_service.get(cache_key)
    if cached:
        return SearchResponse(**cached)

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

    return response


@router.get("/{ticker}", response_model=StockInfo, summary="종목 상세 정보")
async def get_stock_info(ticker: str):
    """
    종목 코드로 주가, 펀더멘털, 투자자 동향, 공매도 정보를 조회합니다.
    종목코드 예: 005930 (삼성전자), 000660 (SK하이닉스)
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


@router.get("/{ticker}/analysis", response_model=AnalysisResult, summary="AI 심층 분석")
async def get_stock_analysis(ticker: str):
    """
    Claude AI를 사용한 4가지 심층 분석을 제공합니다:
    - 기술적 분석 (추세, 지지/저항선, RSI)
    - 펀더멘털 분석 (밸류에이션, 성장성, 재무 건전성)
    - 숨겨진 인사이트 (스마트 머니, 이상 징후)
    - 센티먼트 분석 (뉴스, 공시, 투자자 심리)

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


@router.get("/{ticker}/news", response_model=NewsResponse, summary="뉴스 및 공시")
async def get_stock_news(
    ticker: str,
    limit: int = Query(15, ge=1, le=30, description="반환할 최대 항목 수"),
):
    """
    종목 관련 최신 뉴스와 OpenDART 공시를 조회합니다.
    뉴스: 네이버 금융 / 공시: OpenDART
    """
    ticker = normalize_ticker(ticker)
    if not is_valid_ticker(ticker):
        raise HTTPException(status_code=400, detail="유효하지 않은 종목코드입니다.")

    # 캐시 확인
    cache_key = cache_key_news(ticker)
    cached = await cache_service.get(cache_key)
    if cached:
        return NewsResponse(**cached)

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

    return response


@router.get("/{ticker}/signals", summary="숨겨진 인사이트 신호")
async def get_stock_signals(ticker: str):
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
        return cached

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

    return response
