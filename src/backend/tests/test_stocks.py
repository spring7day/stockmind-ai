"""
StockMind AI — 주식 라우터 테스트
pytest + httpx AsyncClient를 사용한 비동기 API 테스트
실행: pytest tests/ -v
"""
import pytest
from httpx import AsyncClient, ASGITransport

from main import app


# ────────────────────────────────────────────────
# 픽스처
# ────────────────────────────────────────────────

@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    """테스트용 AsyncClient. 실제 서버 없이 ASGI 앱을 직접 호출합니다."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ────────────────────────────────────────────────
# Health Check
# ────────────────────────────────────────────────

@pytest.mark.anyio
async def test_health_check(client: AsyncClient):
    """서버 상태 확인 엔드포인트 테스트"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data
    assert "version" in data


@pytest.mark.anyio
async def test_root(client: AsyncClient):
    """루트 엔드포인트 테스트"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "StockMind AI API"


# ────────────────────────────────────────────────
# 종목 검색
# ────────────────────────────────────────────────

@pytest.mark.anyio
async def test_search_stocks_valid(client: AsyncClient):
    """유효한 검색어로 종목 검색"""
    response = await client.get("/api/stocks/search?q=삼성")
    # 종목 목록 로드 여부에 따라 결과가 달라질 수 있으므로 200만 확인
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "results" in data
    assert "total" in data
    assert data["query"] == "삼성"


@pytest.mark.anyio
async def test_search_stocks_empty_query(client: AsyncClient):
    """빈 검색어 처리 — 422 반환 예상"""
    response = await client.get("/api/stocks/search?q=")
    # FastAPI 유효성 검사로 422 또는 400
    assert response.status_code in (400, 422)


# ────────────────────────────────────────────────
# 종목 상세 정보
# ────────────────────────────────────────────────

@pytest.mark.anyio
async def test_get_stock_invalid_ticker(client: AsyncClient):
    """유효하지 않은 종목코드 처리"""
    response = await client.get("/api/stocks/INVALID")
    # 코드 정규화 후 숫자가 아니면 400
    assert response.status_code == 400


@pytest.mark.anyio
async def test_get_stock_ticker_normalization(client: AsyncClient):
    """종목코드 정규화 테스트 (5930 → 005930)"""
    # 짧은 코드도 허용 (내부에서 0 패딩)
    response = await client.get("/api/stocks/5930")
    # 404 (종목 없음) 또는 200이면 정규화 성공
    assert response.status_code in (200, 404)


# ────────────────────────────────────────────────
# 관심종목
# ────────────────────────────────────────────────

@pytest.mark.anyio
async def test_watchlist_empty(client: AsyncClient):
    """빈 관심종목 목록 조회"""
    response = await client.get("/api/watchlist")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.anyio
async def test_watchlist_add_invalid_ticker(client: AsyncClient):
    """유효하지 않은 종목코드 추가 시도"""
    response = await client.post("/api/watchlist", json={"ticker": "INVALID"})
    assert response.status_code == 400


# ────────────────────────────────────────────────
# 유틸리티 함수 단위 테스트
# ────────────────────────────────────────────────

def test_normalize_ticker():
    """종목코드 정규화 함수 테스트"""
    from app.utils.helpers import normalize_ticker

    assert normalize_ticker("5930") == "005930"
    assert normalize_ticker("005930") == "005930"
    assert normalize_ticker("  005930  ") == "005930"
    assert normalize_ticker("1") == "000001"


def test_is_valid_ticker():
    """종목코드 유효성 검사 함수 테스트"""
    from app.utils.helpers import is_valid_ticker

    assert is_valid_ticker("005930") is True
    assert is_valid_ticker("000660") is True
    assert is_valid_ticker("INVALID") is False
    assert is_valid_ticker("12345") is False  # 5자리
    assert is_valid_ticker("1234567") is False  # 7자리


def test_format_price():
    """가격 포맷 함수 테스트"""
    from app.utils.helpers import format_price

    assert format_price(1234567) == "1,234,567원"
    assert format_price(None) == "-"
    assert format_price(0) == "0원"


def test_format_market_cap():
    """시가총액 포맷 테스트"""
    from app.utils.helpers import format_market_cap

    assert "조원" in format_market_cap(400e12)  # 400조
    assert "억원" in format_market_cap(5000e8)  # 5000억
    assert format_market_cap(None) == "-"


def test_safe_divide():
    """안전한 나눗셈 테스트"""
    from app.utils.helpers import safe_divide

    assert safe_divide(10, 2) == 5.0
    assert safe_divide(10, 0) is None
    assert safe_divide(None, 5) is None
    assert safe_divide(5, None) is None


def test_korean_date_to_iso():
    """날짜 형식 변환 테스트"""
    from app.utils.helpers import korean_date_to_iso

    assert korean_date_to_iso("20240315") == "2024-03-15"
    assert korean_date_to_iso("20241231") == "2024-12-31"
    assert korean_date_to_iso(None) is None
    assert korean_date_to_iso("invalid") == "invalid"  # 변환 불가 시 원본 반환
