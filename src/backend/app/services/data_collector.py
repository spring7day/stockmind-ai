"""
StockMind AI — 한국 주식 데이터 수집 서비스
pykrx, yfinance, OpenDART API를 활용하여 주식 데이터를 수집합니다.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
import pandas as pd
from pykrx import stock as krx

from app.config import settings
from app.models.stock import (
    InvestorTrading,
    NewsItem,
    ShortSelling,
    StockFundamentals,
    StockInfo,
    StockPrice,
    StockSearchResult,
)

logger = logging.getLogger(__name__)

# KOSPI/KOSDAQ 전체 종목 캐시 (앱 시작 시 로드)
_stock_list_cache: Optional[Dict[str, Dict]] = None


def _get_today() -> str:
    """오늘 날짜를 YYYYMMDD 형식으로 반환"""
    return datetime.now().strftime("%Y%m%d")


def _get_date_n_days_ago(n: int) -> str:
    """n일 전 날짜를 YYYYMMDD 형식으로 반환"""
    return (datetime.now() - timedelta(days=n)).strftime("%Y%m%d")


# 주요 한국 주식 fallback 목록 (pykrx 해외 접근 불가 시 사용)
_FALLBACK_STOCK_LIST: Dict[str, Dict] = {
    # KOSPI 대형주
    "005930": {"name": "삼성전자", "market": "KOSPI"},
    "000660": {"name": "SK하이닉스", "market": "KOSPI"},
    "373220": {"name": "LG에너지솔루션", "market": "KOSPI"},
    "207940": {"name": "삼성바이오로직스", "market": "KOSPI"},
    "005380": {"name": "현대차", "market": "KOSPI"},
    "000270": {"name": "기아", "market": "KOSPI"},
    "005490": {"name": "POSCO홀딩스", "market": "KOSPI"},
    "035420": {"name": "NAVER", "market": "KOSPI"},
    "006400": {"name": "삼성SDI", "market": "KOSPI"},
    "051910": {"name": "LG화학", "market": "KOSPI"},
    "012330": {"name": "현대모비스", "market": "KOSPI"},
    "035720": {"name": "카카오", "market": "KOSPI"},
    "105560": {"name": "KB금융", "market": "KOSPI"},
    "055550": {"name": "신한지주", "market": "KOSPI"},
    "086790": {"name": "하나금융지주", "market": "KOSPI"},
    "028260": {"name": "삼성물산", "market": "KOSPI"},
    "066570": {"name": "LG전자", "market": "KOSPI"},
    "017670": {"name": "SK텔레콤", "market": "KOSPI"},
    "033780": {"name": "KT&G", "market": "KOSPI"},
    "010130": {"name": "고려아연", "market": "KOSPI"},
    "068270": {"name": "셀트리온", "market": "KOSPI"},
    "032830": {"name": "삼성생명", "market": "KOSPI"},
    "034020": {"name": "두산에너빌리티", "market": "KOSPI"},
    "329180": {"name": "HD현대중공업", "market": "KOSPI"},
    "138040": {"name": "메리츠금융지주", "market": "KOSPI"},
    "267250": {"name": "HD현대", "market": "KOSPI"},
    "096770": {"name": "SK이노베이션", "market": "KOSPI"},
    "011170": {"name": "롯데케미칼", "market": "KOSPI"},
    "009150": {"name": "삼성전기", "market": "KOSPI"},
    "090430": {"name": "아모레퍼시픽", "market": "KOSPI"},
    "003550": {"name": "LG", "market": "KOSPI"},
    "034730": {"name": "SK", "market": "KOSPI"},
    "015760": {"name": "한국전력", "market": "KOSPI"},
    "000810": {"name": "삼성화재", "market": "KOSPI"},
    "030200": {"name": "KT", "market": "KOSPI"},
    "018880": {"name": "한온시스템", "market": "KOSPI"},
    "010950": {"name": "S-Oil", "market": "KOSPI"},
    "011200": {"name": "HMM", "market": "KOSPI"},
    "032640": {"name": "LG유플러스", "market": "KOSPI"},
    "003490": {"name": "대한항공", "market": "KOSPI"},
    "024110": {"name": "기업은행", "market": "KOSPI"},
    "000100": {"name": "유한양행", "market": "KOSPI"},
    "128940": {"name": "한미약품", "market": "KOSPI"},
    "009540": {"name": "HD한국조선해양", "market": "KOSPI"},
    "042660": {"name": "한화오션", "market": "KOSPI"},
    "000720": {"name": "현대건설", "market": "KOSPI"},
    "006360": {"name": "GS건설", "market": "KOSPI"},
    "028050": {"name": "삼성엔지니어링", "market": "KOSPI"},
    "047050": {"name": "포스코인터내셔널", "market": "KOSPI"},
    "180640": {"name": "한화에어로스페이스", "market": "KOSPI"},
    "012450": {"name": "한화시스템", "market": "KOSPI"},
    "000830": {"name": "삼성물산우B", "market": "KOSPI"},
    "086280": {"name": "현대글로비스", "market": "KOSPI"},
    "161390": {"name": "한국타이어앤테크놀로지", "market": "KOSPI"},
    "004020": {"name": "현대제철", "market": "KOSPI"},
    "001040": {"name": "CJ", "market": "KOSPI"},
    "097950": {"name": "CJ제일제당", "market": "KOSPI"},
    "000080": {"name": "하이트진로", "market": "KOSPI"},
    "021240": {"name": "코웨이", "market": "KOSPI"},
    "011780": {"name": "금호석유", "market": "KOSPI"},
    "016360": {"name": "삼성증권", "market": "KOSPI"},
    "071050": {"name": "한국금융지주", "market": "KOSPI"},
    "139480": {"name": "이마트", "market": "KOSPI"},
    "004170": {"name": "신세계", "market": "KOSPI"},
    "023530": {"name": "롯데쇼핑", "market": "KOSPI"},
    "010140": {"name": "삼성중공업", "market": "KOSPI"},
    "009830": {"name": "한화솔루션", "market": "KOSPI"},
    "014830": {"name": "유니드", "market": "KOSPI"},
    "000120": {"name": "CJ대한통운", "market": "KOSPI"},
    "003080": {"name": "성보화학", "market": "KOSPI"},
    "002790": {"name": "아모레G", "market": "KOSPI"},
    "007070": {"name": "GS리테일", "market": "KOSPI"},
    "036570": {"name": "엔씨소프트", "market": "KOSPI"},
    "251270": {"name": "넷마블", "market": "KOSPI"},
    "259960": {"name": "크래프톤", "market": "KOSPI"},
    "034220": {"name": "LG디스플레이", "market": "KOSPI"},
    "006800": {"name": "미래에셋증권", "market": "KOSPI"},
    "003620": {"name": "쌍용C&E", "market": "KOSPI"},
    "004000": {"name": "롯데정밀화학", "market": "KOSPI"},
    "025860": {"name": "남해화학", "market": "KOSPI"},
    "001800": {"name": "오리온홀딩스", "market": "KOSPI"},
    "271560": {"name": "오리온", "market": "KOSPI"},
    "000070": {"name": "삼양홀딩스", "market": "KOSPI"},
    "145720": {"name": "덴티움", "market": "KOSPI"},
    "069960": {"name": "현대백화점", "market": "KOSPI"},
    "008770": {"name": "호텔신라", "market": "KOSPI"},
    "002380": {"name": "KCC", "market": "KOSPI"},
    "011790": {"name": "SKC", "market": "KOSPI"},
    "005070": {"name": "코스모신소재", "market": "KOSPI"},
    "010060": {"name": "OCI홀딩스", "market": "KOSPI"},
    "005945": {"name": "NH투자증권", "market": "KOSPI"},
    "016880": {"name": "웅진씽크빅", "market": "KOSPI"},
    "019170": {"name": "신풍제약", "market": "KOSPI"},
    "006650": {"name": "대한유화", "market": "KOSPI"},
    "298040": {"name": "효성중공업", "market": "KOSPI"},
    "298000": {"name": "효성티앤씨", "market": "KOSPI"},
    "000210": {"name": "DL", "market": "KOSPI"},
    "000215": {"name": "DL우", "market": "KOSPI"},
    "078930": {"name": "GS", "market": "KOSPI"},
    "088350": {"name": "한화생명", "market": "KOSPI"},
    "000240": {"name": "한국타이어앤테크놀로지", "market": "KOSPI"},
    "316140": {"name": "우리금융지주", "market": "KOSPI"},
    "175330": {"name": "JB금융지주", "market": "KOSPI"},
    "192820": {"name": "코스맥스", "market": "KOSPI"},
    "003000": {"name": "부광약품", "market": "KOSPI"},
    "006990": {"name": "코리아써키트", "market": "KOSPI"},
    # KOSDAQ 대형주
    "247540": {"name": "에코프로비엠", "market": "KOSDAQ"},
    "086520": {"name": "에코프로", "market": "KOSDAQ"},
    "028300": {"name": "HLB", "market": "KOSDAQ"},
    "091990": {"name": "셀트리온헬스케어", "market": "KOSDAQ"},
    "293490": {"name": "카카오게임즈", "market": "KOSDAQ"},
    "263750": {"name": "펄어비스", "market": "KOSDAQ"},
    "112040": {"name": "위메이드", "market": "KOSDAQ"},
    "357780": {"name": "솔브레인", "market": "KOSDAQ"},
    "039030": {"name": "이오테크닉스", "market": "KOSDAQ"},
    "041510": {"name": "에스엠", "market": "KOSDAQ"},
    "035900": {"name": "JYP Ent.", "market": "KOSDAQ"},
    "122870": {"name": "와이지엔터테인먼트", "market": "KOSDAQ"},
    "348150": {"name": "교촌에프앤비", "market": "KOSDAQ"},
    "214150": {"name": "클래시스", "market": "KOSDAQ"},
    "145020": {"name": "휴젤", "market": "KOSDAQ"},
    "196170": {"name": "알테오젠", "market": "KOSDAQ"},
    "011560": {"name": "세방전지", "market": "KOSDAQ"},
    "237690": {"name": "에스티팜", "market": "KOSDAQ"},
    "319660": {"name": "피에스케이", "market": "KOSDAQ"},
    "403870": {"name": "HPSP", "market": "KOSDAQ"},
    "067160": {"name": "아프리카TV", "market": "KOSDAQ"},
    "060280": {"name": "큐렉소", "market": "KOSDAQ"},
    "032500": {"name": "케이엠더블유", "market": "KOSDAQ"},
    "095340": {"name": "ISC", "market": "KOSDAQ"},
    "058470": {"name": "리노공업", "market": "KOSDAQ"},
    "950130": {"name": "엑스페릭스", "market": "KOSDAQ"},
    "054040": {"name": "한국컴퓨터", "market": "KOSDAQ"},
    "045300": {"name": "성우하이텍", "market": "KOSDAQ"},
    "064760": {"name": "티씨케이", "market": "KOSDAQ"},
    "091700": {"name": "파트론", "market": "KOSDAQ"},
    "036540": {"name": "SFA반도체", "market": "KOSDAQ"},
    "041960": {"name": "코미팜", "market": "KOSDAQ"},
    "078340": {"name": "컴투스", "market": "KOSDAQ"},
    "052260": {"name": "씨앤씨인터내셔널", "market": "KOSDAQ"},
    "950160": {"name": "코오롱티슈진", "market": "KOSDAQ"},
    "018290": {"name": "브이티", "market": "KOSDAQ"},
    "222080": {"name": "씨아이에스", "market": "KOSDAQ"},
    "228760": {"name": "지놈앤컴퍼니", "market": "KOSDAQ"},
    "066970": {"name": "엘앤에프", "market": "KOSDAQ"},
    "336370": {"name": "솔루스첨단소재", "market": "KOSDAQ"},
    "323990": {"name": "아피메즈", "market": "KOSDAQ"},
    "352820": {"name": "하이브", "market": "KOSDAQ"},
    "258610": {"name": "케이엔더블유", "market": "KOSDAQ"},
    "039440": {"name": "에스티아이", "market": "KOSDAQ"},
    "241560": {"name": "두산퓨얼셀", "market": "KOSDAQ"},
    "039200": {"name": "오스코텍", "market": "KOSDAQ"},
    "115180": {"name": "큐리언트", "market": "KOSDAQ"},
    "298380": {"name": "에이비엘바이오", "market": "KOSDAQ"},
    "214370": {"name": "케어젠", "market": "KOSDAQ"},
    "226950": {"name": "올릭스", "market": "KOSDAQ"},
    "950170": {"name": "JTC", "market": "KOSDAQ"},
    "204840": {"name": "지엔씨에너지", "market": "KOSDAQ"},
    "950210": {"name": "프레스티지바이오파마", "market": "KOSDAQ"},
}


async def load_stock_list() -> Dict[str, Dict]:
    """
    KOSPI + KOSDAQ 전체 종목 목록을 pykrx에서 로드합니다.
    pykrx 접근 실패 또는 결과가 50개 미만이면 하드코딩 fallback 목록을 사용합니다.
    반환값: {ticker: {name, market}} 형태의 딕셔너리
    """
    global _stock_list_cache
    if _stock_list_cache is not None:
        return _stock_list_cache

    def _fetch_list():
        today = _get_today()
        stocks = {}
        # KOSPI 종목
        try:
            kospi_tickers = krx.get_market_ticker_list(today, market="KOSPI")
            for ticker in kospi_tickers:
                name = krx.get_market_ticker_name(ticker)
                stocks[ticker] = {"name": name, "market": "KOSPI"}
        except Exception as e:
            logger.warning(f"KOSPI 종목 목록 로드 실패: {e}")

        # KOSDAQ 종목
        try:
            kosdaq_tickers = krx.get_market_ticker_list(today, market="KOSDAQ")
            for ticker in kosdaq_tickers:
                name = krx.get_market_ticker_name(ticker)
                stocks[ticker] = {"name": name, "market": "KOSDAQ"}
        except Exception as e:
            logger.warning(f"KOSDAQ 종목 목록 로드 실패: {e}")

        return stocks

    loop = asyncio.get_running_loop()
    pykrx_result = await loop.run_in_executor(None, _fetch_list)

    if len(pykrx_result) >= 50:
        # pykrx 결과가 충분하면 fallback과 merge (fallback이 기본값, pykrx가 우선)
        result = {**_FALLBACK_STOCK_LIST, **pykrx_result}
        logger.info(f"pykrx 종목 목록 로드 성공: {len(pykrx_result)}개 (fallback 포함 {len(result)}개)")
    else:
        # pykrx 실패 또는 결과 부족 → fallback 사용
        logger.warning(
            f"pykrx 종목 목록 부족({len(pykrx_result)}개 < 50개), "
            f"fallback 목록 사용 ({len(_FALLBACK_STOCK_LIST)}개)"
        )
        result = {**_FALLBACK_STOCK_LIST, **pykrx_result}

    _stock_list_cache = result
    logger.info(f"종목 목록 로드 완료: {len(result)}개")
    return result


def search_stocks(query: str, limit: int = 20) -> List[StockSearchResult]:
    """
    종목명 또는 종목코드로 검색합니다.
    _stock_list_cache에서 검색하므로 load_stock_list()가 먼저 호출되어야 합니다.
    """
    if _stock_list_cache is None:
        return []

    query_lower = query.lower()
    results = []

    for ticker, info in _stock_list_cache.items():
        name = info["name"]
        # 종목코드 또는 종목명에서 검색
        if query in ticker or query_lower in name.lower():
            results.append(
                StockSearchResult(
                    ticker=ticker,
                    name=name,
                    market=info["market"],
                )
            )
        if len(results) >= limit:
            break

    return results


async def get_stock_price(ticker: str) -> Optional[StockPrice]:
    """
    pykrx로 현재 주가 데이터를 수집합니다.
    장 마감 후에는 당일 종가 기준으로 반환합니다.
    """
    def _fetch():
        today = _get_today()
        start = _get_date_n_days_ago(5)  # 주말/공휴일 고려 5일 전부터 조회

        try:
            # OHLCV 데이터 (시가/고가/저가/종가/거래량)
            df = krx.get_market_ohlcv_by_date(start, today, ticker)
            if df.empty:
                return None

            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) >= 2 else None

            current = float(latest["종가"])
            prev_close = float(prev["종가"]) if prev is not None else current
            change = current - prev_close
            change_pct = (change / prev_close * 100) if prev_close != 0 else 0.0

            # 거래대금 = 종가 × 거래량 (pykrx는 거래대금도 제공하나 컬럼명 확인)
            trading_value = None
            if "거래대금" in latest:
                trading_value = float(latest["거래대금"])

            return StockPrice(
                current=current,
                open=float(latest["시가"]),
                high=float(latest["고가"]),
                low=float(latest["저가"]),
                prev_close=prev_close,
                change=change,
                change_pct=round(change_pct, 2),
                volume=int(latest["거래량"]),
                trading_value=trading_value,
            )
        except Exception as e:
            logger.error(f"[{ticker}] 주가 수집 실패: {e}")
            return None

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _fetch)


async def get_stock_fundamentals(ticker: str) -> Optional[StockFundamentals]:
    """
    pykrx로 펀더멘털 데이터(PER, PBR, EPS 등)를 수집합니다.
    """
    def _fetch():
        today = _get_today()
        start = _get_date_n_days_ago(5)

        try:
            # 시가총액 및 PER, PBR, EPS (pykrx get_market_fundamental)
            df = krx.get_market_fundamental_by_date(start, today, ticker)
            if df.empty:
                return None

            latest = df.iloc[-1]

            # 시가총액
            cap_df = krx.get_market_cap_by_date(start, today, ticker)
            market_cap = None
            if not cap_df.empty:
                market_cap = float(cap_df.iloc[-1]["시가총액"])

            return StockFundamentals(
                market_cap=market_cap,
                per=_safe_float(latest.get("PER")),
                pbr=_safe_float(latest.get("PBR")),
                eps=_safe_float(latest.get("EPS")),
                dividend_yield=_safe_float(latest.get("DIV")),
            )
        except Exception as e:
            logger.error(f"[{ticker}] 펀더멘털 수집 실패: {e}")
            return None

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _fetch)


async def get_investor_trading(ticker: str) -> Optional[InvestorTrading]:
    """
    pykrx로 기관/외국인/개인 순매수 데이터를 수집합니다.
    """
    def _fetch():
        today = _get_today()
        start = _get_date_n_days_ago(3)

        try:
            # 투자자별 거래 데이터
            df = krx.get_market_trading_value_by_date(start, today, ticker)
            if df.empty:
                return None

            latest = df.iloc[-1]
            date_str = df.index[-1].strftime("%Y%m%d") if hasattr(df.index[-1], "strftime") else str(df.index[-1])

            return InvestorTrading(
                institutional=_safe_float(latest.get("기관합계")),
                foreign=_safe_float(latest.get("외국인합계")),
                retail=_safe_float(latest.get("개인")),
                date=date_str,
            )
        except Exception as e:
            logger.error(f"[{ticker}] 투자자 거래 수집 실패: {e}")
            return None

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _fetch)


async def get_short_selling(ticker: str) -> Optional[ShortSelling]:
    """
    pykrx로 공매도 비율 데이터를 수집합니다.
    """
    def _fetch():
        today = _get_today()
        start = _get_date_n_days_ago(5)

        try:
            df = krx.get_shorting_volume_by_date(start, today, ticker)
            if df.empty:
                return None

            latest = df.iloc[-1]
            date_str = df.index[-1].strftime("%Y%m%d") if hasattr(df.index[-1], "strftime") else str(df.index[-1])

            # 공매도 비율 계산 (공매도 거래량 / 전체 거래량)
            short_vol = _safe_float(latest.get("공매도"))
            total_vol = _safe_float(latest.get("총거래량"))
            ratio = (short_vol / total_vol * 100) if (short_vol and total_vol and total_vol > 0) else None

            return ShortSelling(
                short_ratio=round(ratio, 2) if ratio else None,
                short_balance=short_vol,
                date=date_str,
            )
        except Exception as e:
            logger.error(f"[{ticker}] 공매도 수집 실패: {e}")
            return None

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _fetch)


async def get_full_stock_info(ticker: str) -> Optional[StockInfo]:
    """
    주식의 전체 정보(가격, 펀더멘털, 투자자 거래, 공매도)를 병렬로 수집합니다.
    """
    # 종목 기본 정보 확인
    stock_list = await load_stock_list()
    if ticker not in stock_list:
        logger.warning(f"[{ticker}] 종목을 찾을 수 없습니다.")
        return None

    info = stock_list[ticker]

    # 4가지 데이터 병렬 수집
    price, fundamentals, investor_trading, short_selling = await asyncio.gather(
        get_stock_price(ticker),
        get_stock_fundamentals(ticker),
        get_investor_trading(ticker),
        get_short_selling(ticker),
        return_exceptions=True,
    )

    # 예외 처리 (gather에서 예외가 반환된 경우)
    if isinstance(price, Exception):
        logger.error(f"[{ticker}] 가격 수집 예외: {price}")
        price = None
    if isinstance(fundamentals, Exception):
        fundamentals = None
    if isinstance(investor_trading, Exception):
        investor_trading = None
    if isinstance(short_selling, Exception):
        short_selling = None

    return StockInfo(
        ticker=ticker,
        name=info["name"],
        market=info["market"],
        price=price,
        fundamentals=fundamentals,
        investor_trading=investor_trading,
        short_selling=short_selling,
    )


async def get_dart_disclosures(ticker: str, limit: int = 10) -> List[NewsItem]:
    """
    OpenDART API로 공시 정보를 수집합니다.
    DART_API_KEY 환경변수가 없으면 빈 목록을 반환합니다.
    """
    if not settings.DART_API_KEY:
        logger.warning("DART_API_KEY가 설정되지 않아 공시 수집을 건너뜁니다.")
        return []

    # 6자리 종목코드 → DART corp_code 조회 필요 (간소화: 종목코드로 직접 조회)
    url = f"{settings.DART_BASE_URL}/list.json"
    params = {
        "crtfc_key": settings.DART_API_KEY,
        "stock_code": ticker,
        "bgn_de": _get_date_n_days_ago(30),
        "end_de": _get_today(),
        "page_count": limit,
        "sort": "date",
        "sort_mth": "desc",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        if data.get("status") != "000":
            logger.warning(f"[{ticker}] DART API 응답 오류: {data.get('message')}")
            return []

        items = []
        for item in data.get("list", [])[:limit]:
            items.append(
                NewsItem(
                    title=item.get("report_nm", ""),
                    source="OpenDART",
                    url=f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={item.get('rcept_no', '')}",
                    published_at=item.get("rcept_dt"),
                    is_disclosure=True,
                )
            )
        return items

    except Exception as e:
        logger.error(f"[{ticker}] DART 공시 수집 실패: {e}")
        return []


async def get_stock_news(ticker: str, company_name: str) -> List[NewsItem]:
    """
    네이버 금융 뉴스에서 종목 관련 뉴스를 스크래핑합니다.
    BeautifulSoup을 사용한 간단한 스크래퍼입니다.
    """
    from bs4 import BeautifulSoup

    url = f"https://finance.naver.com/item/news_news.nhn?code={ticker}&page=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; StockMindBot/1.0)",
        "Accept-Language": "ko-KR,ko;q=0.9",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")
        news_items = []

        # 네이버 금융 뉴스 테이블 파싱
        rows = soup.select("table.type5 tr")
        for row in rows:
            title_tag = row.select_one("td.title a")
            date_tag = row.select_one("td.date")
            source_tag = row.select_one("td.info")

            if not title_tag:
                continue

            href = title_tag.get("href", "")
            full_url = f"https://finance.naver.com{href}" if href.startswith("/") else href

            news_items.append(
                NewsItem(
                    title=title_tag.get_text(strip=True),
                    source=source_tag.get_text(strip=True) if source_tag else "네이버금융",
                    url=full_url,
                    published_at=date_tag.get_text(strip=True) if date_tag else None,
                    is_disclosure=False,
                )
            )

        return news_items[:10]

    except Exception as e:
        logger.error(f"[{ticker}] 뉴스 수집 실패: {e}")
        return []


def _safe_float(value: Any) -> Optional[float]:
    """값을 float으로 안전하게 변환합니다. 변환 불가 시 None 반환."""
    try:
        f = float(value)
        # NaN, Inf 처리
        if f != f or abs(f) == float("inf"):
            return None
        return f
    except (TypeError, ValueError):
        return None
