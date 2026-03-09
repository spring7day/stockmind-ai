"""
StockMind AI — 공통 유틸리티 함수
"""
import re
from datetime import datetime
from typing import Optional


def normalize_ticker(ticker: str) -> str:
    """
    종목 코드를 6자리로 정규화합니다.
    예: '5930' → '005930', '005930' → '005930'
    """
    ticker = ticker.strip().upper()
    # 숫자만 남기기
    digits = re.sub(r"\D", "", ticker)
    return digits.zfill(6)


def is_valid_ticker(ticker: str) -> bool:
    """종목 코드가 유효한 6자리 숫자인지 확인합니다."""
    return bool(re.fullmatch(r"\d{6}", ticker))


def format_price(price: Optional[float]) -> str:
    """가격을 한국식 원화 표기로 포맷합니다. 예: 1234567 → '1,234,567원'"""
    if price is None:
        return "-"
    return f"{price:,.0f}원"


def format_change_pct(pct: Optional[float]) -> str:
    """등락률을 포맷합니다. 예: 2.35 → '+2.35%', -1.2 → '-1.20%'"""
    if pct is None:
        return "-"
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.2f}%"


def format_market_cap(cap: Optional[float]) -> str:
    """시가총액을 조/억 단위로 포맷합니다."""
    if cap is None:
        return "-"
    if cap >= 1e12:
        return f"{cap / 1e12:.1f}조원"
    elif cap >= 1e8:
        return f"{cap / 1e8:.0f}억원"
    else:
        return f"{cap:,.0f}원"


def korean_date_to_iso(date_str: Optional[str]) -> Optional[str]:
    """
    YYYYMMDD 형식의 날짜를 ISO 8601 형식으로 변환합니다.
    예: '20240315' → '2024-03-15'
    """
    if not date_str or len(date_str) != 8:
        return date_str
    try:
        dt = datetime.strptime(date_str, "%Y%m%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return date_str


def truncate_text(text: str, max_length: int = 100) -> str:
    """텍스트를 지정한 길이로 자르고 '...'을 붙입니다."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def safe_divide(numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
    """0으로 나누기를 방지하는 안전한 나눗셈."""
    if numerator is None or denominator is None or denominator == 0:
        return None
    return numerator / denominator


def get_market_status() -> dict:
    """
    현재 한국 주식 시장 개장 여부를 반환합니다.
    장 시간: 평일 09:00 ~ 15:30 KST
    """
    import zoneinfo

    kst = zoneinfo.ZoneInfo("Asia/Seoul")
    now = datetime.now(tz=kst)

    is_weekday = now.weekday() < 5  # 0=월요일, 4=금요일
    market_open = now.replace(hour=9, minute=0, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
    is_open = is_weekday and market_open <= now <= market_close

    return {
        "is_open": is_open,
        "current_time_kst": now.strftime("%Y-%m-%d %H:%M:%S"),
        "market_open": "09:00",
        "market_close": "15:30",
    }


def build_error_response(code: str, message: str, detail: Optional[str] = None) -> dict:
    """표준 에러 응답 딕셔너리를 생성합니다."""
    resp = {"error": {"code": code, "message": message}}
    if detail:
        resp["error"]["detail"] = detail
    return resp
