"""
StockMind AI — 관심종목 (Watchlist) API 라우터
Phase 1 MVP: 세션 기반 in-memory 관심종목 (로그인 없이 사용)
Phase 2에서 DB + 사용자 인증 연동 예정
"""
import logging
from datetime import datetime
from typing import Dict

from fastapi import APIRouter, HTTPException

from app.models.stock import WatchlistAddRequest, WatchlistItem, WatchlistResponse
from app.services import data_collector
from app.utils.helpers import is_valid_ticker, normalize_ticker

logger = logging.getLogger(__name__)

router = APIRouter()

# MVP: 서버 메모리에 관심종목 저장 (재시작 시 초기화됨)
# Phase 2: DB로 마이그레이션 예정
_watchlist: Dict[str, WatchlistItem] = {}


@router.get("", response_model=WatchlistResponse, summary="관심종목 목록 조회")
async def get_watchlist():
    """
    저장된 관심종목 목록을 현재 주가와 함께 반환합니다.
    """
    if not _watchlist:
        return WatchlistResponse(items=[], total=0)

    # 현재 주가 업데이트
    import asyncio

    tickers = list(_watchlist.keys())
    price_tasks = [data_collector.get_stock_price(t) for t in tickers]
    prices = await asyncio.gather(*price_tasks, return_exceptions=True)

    updated_items = []
    for ticker, price in zip(tickers, prices):
        item = _watchlist[ticker].model_copy()
        if not isinstance(price, Exception) and price is not None:
            item.current_price = price.current
            item.change_pct = price.change_pct
        updated_items.append(item)

    return WatchlistResponse(items=updated_items, total=len(updated_items))


@router.post("", response_model=WatchlistItem, status_code=201, summary="관심종목 추가")
async def add_to_watchlist(request: WatchlistAddRequest):
    """
    관심종목을 추가합니다. 이미 추가된 종목이면 알림 가격만 업데이트합니다.
    """
    ticker = normalize_ticker(request.ticker)
    if not is_valid_ticker(ticker):
        raise HTTPException(status_code=400, detail="유효하지 않은 종목코드입니다. 6자리 숫자를 입력해주세요.")

    # 종목 존재 확인
    stock_list = await data_collector.load_stock_list()
    if ticker not in stock_list:
        raise HTTPException(status_code=404, detail=f"종목 {ticker}을(를) 찾을 수 없습니다.")

    stock_info = stock_list[ticker]

    # 이미 있으면 알림 가격 업데이트
    if ticker in _watchlist:
        item = _watchlist[ticker]
        if request.alert_price is not None:
            item.alert_price = request.alert_price
        return item

    # 현재 주가 조회
    current_price = None
    change_pct = None
    try:
        price = await data_collector.get_stock_price(ticker)
        if price:
            current_price = price.current
            change_pct = price.change_pct
    except Exception as e:
        logger.warning(f"[{ticker}] 관심종목 추가 시 주가 조회 실패: {e}")

    item = WatchlistItem(
        ticker=ticker,
        name=stock_info["name"],
        market=stock_info["market"],
        added_at=datetime.utcnow(),
        current_price=current_price,
        change_pct=change_pct,
        alert_price=request.alert_price,
    )

    _watchlist[ticker] = item
    logger.info(f"관심종목 추가: {ticker} ({stock_info['name']})")

    return item


@router.delete("/{ticker}", status_code=204, summary="관심종목 삭제")
async def remove_from_watchlist(ticker: str):
    """관심종목에서 종목을 삭제합니다."""
    ticker = normalize_ticker(ticker)

    if ticker not in _watchlist:
        raise HTTPException(status_code=404, detail=f"관심종목에 {ticker}이(가) 없습니다.")

    del _watchlist[ticker]
    logger.info(f"관심종목 삭제: {ticker}")
    # 204 No Content — 응답 본문 없음


@router.patch("/{ticker}/alert", response_model=WatchlistItem, summary="알림 가격 설정")
async def update_alert_price(ticker: str, alert_price: float):
    """
    관심종목의 알림 가격을 업데이트합니다.
    해당 가격 도달 시 알림을 제공할 예정입니다 (Phase 2).
    """
    ticker = normalize_ticker(ticker)

    if ticker not in _watchlist:
        raise HTTPException(status_code=404, detail=f"관심종목에 {ticker}이(가) 없습니다.")

    if alert_price <= 0:
        raise HTTPException(status_code=400, detail="알림 가격은 0보다 커야 합니다.")

    _watchlist[ticker].alert_price = alert_price
    return _watchlist[ticker]
