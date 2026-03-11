"""
StockMind AI — 한국 주식 데이터 수집 서비스
FinanceDataReader와 정적 종목 목록(stocks.json)을 활용하여 주식 데이터를 수집합니다.
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import FinanceDataReader as fdr
import httpx
import pandas as pd

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

# stocks.json 경로
_STOCKS_JSON_PATH = Path(__file__).parent.parent / "data" / "stocks.json"


def _get_today() -> str:
    """오늘 날짜를 YYYYMMDD 형식으로 반환"""
    return datetime.now().strftime("%Y%m%d")


def _get_date_n_days_ago(n: int) -> str:
    """n일 전 날짜를 YYYYMMDD 형식으로 반환"""
    return (datetime.now() - timedelta(days=n)).strftime("%Y%m%d")


def _get_start_date_for_fetch() -> str:
    """주가 조회 시작일 (10 영업일 여유분을 위해 14일 전)을 YYYY-MM-DD 형식으로 반환"""
    return (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")


async def load_stock_list() -> Dict[str, Dict]:
    """
    stocks.json 파일에서 KOSPI + KOSDAQ 종목 목록을 로드합니다.
    반환값: {ticker: {name, market}} 형태의 딕셔너리
    """
    global _stock_list_cache
    if _stock_list_cache is not None:
        return _stock_list_cache

    def _load():
        try:
            with open(_STOCKS_JSON_PATH, encoding="utf-8") as f:
                items = json.load(f)
            result = {}
            for item in items:
                ticker = item["ticker"]
                result[ticker] = {"name": item["name"], "market": item["market"]}
            logger.info(f"stocks.json 로드 완료: {len(result)}개 종목")
            return result
        except Exception as e:
            logger.error(f"stocks.json 로드 실패: {e}")
            return {}

    loop = asyncio.get_running_loop()
    _stock_list_cache = await loop.run_in_executor(None, _load)
    return _stock_list_cache


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
    FinanceDataReader로 현재 주가 데이터를 수집합니다.
    Redis 캐시(TTL 300초) → fdr.DataReader 요청 순으로 시도합니다.
    """
    from app.services.cache import cache_service

    cache_key = f"price:{ticker}"

    # 캐시 확인
    cached = await cache_service.get(cache_key)
    if cached is not None:
        logger.debug(f"[{ticker}] 주가 캐시 히트")
        return StockPrice(**cached)

    def _fetch() -> Optional[StockPrice]:
        try:
            start_date = _get_start_date_for_fetch()
            df = fdr.DataReader(ticker, start_date)
            if df is None or df.empty:
                logger.warning(f"[{ticker}] fdr.DataReader 결과 없음")
                return None

            if len(df) < 1:
                return None

            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) >= 2 else None

            current = float(latest["Close"])
            prev_close = float(prev["Close"]) if prev is not None else current
            change = current - prev_close
            change_pct = (change / prev_close * 100) if prev_close != 0 else 0.0

            return StockPrice(
                current=current,
                open=float(latest["Open"]),
                high=float(latest["High"]),
                low=float(latest["Low"]),
                prev_close=prev_close,
                change=change,
                change_pct=round(change_pct, 2),
                volume=int(latest["Volume"]),
                trading_value=None,
            )
        except Exception as e:
            logger.error(f"[{ticker}] 주가 수집 실패: {e}")
            return None

    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, _fetch)

    if result is not None:
        await cache_service.set(cache_key, result.model_dump(), ttl=300)

    return result


async def get_stock_fundamentals(ticker: str) -> Optional[StockFundamentals]:
    """
    FinanceDataReader는 PER/PBR 등 펀더멘털 데이터를 제공하지 않으므로 None을 반환합니다.
    향후 OpenDART 또는 다른 API로 교체 가능합니다.
    """
    return None


async def get_investor_trading(ticker: str) -> Optional[InvestorTrading]:
    """
    FinanceDataReader는 기관/외국인/개인 순매수 데이터를 제공하지 않으므로 None을 반환합니다.
    향후 OpenDART 또는 다른 API로 교체 가능합니다.
    """
    return None


async def get_short_selling(ticker: str) -> Optional[ShortSelling]:
    """
    FinanceDataReader는 한국 주식 공매도 비율 데이터를 제공하지 않으므로 None을 반환합니다.
    """
    return None


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

    # 가격 수집 (펀더멘털/투자자거래/공매도는 fdr 미지원)
    price, fundamentals = await asyncio.gather(
        get_stock_price(ticker),
        get_stock_fundamentals(ticker),
        return_exceptions=True,
    )

    # 예외 처리 (gather에서 예외가 반환된 경우)
    if isinstance(price, Exception):
        logger.error(f"[{ticker}] 가격 수집 예외: {price}")
        price = None
    if isinstance(fundamentals, Exception):
        fundamentals = None

    return StockInfo(
        ticker=ticker,
        name=info["name"],
        market=info["market"],
        price=price,
        fundamentals=fundamentals,
        investor_trading=None,
        short_selling=None,
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
