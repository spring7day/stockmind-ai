"""
StockMind AI — 주식 관련 Pydantic 모델 정의
API 요청/응답 및 내부 데이터 구조 정의
"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# ────────────────────────────────────────────────
# 기본 주식 정보
# ────────────────────────────────────────────────

class StockPrice(BaseModel):
    """현재 주가 정보"""
    current: float = Field(..., description="현재가 (원)")
    open: float = Field(..., description="시가")
    high: float = Field(..., description="고가")
    low: float = Field(..., description="저가")
    prev_close: float = Field(..., description="전일 종가")
    change: float = Field(..., description="전일 대비 변화량")
    change_pct: float = Field(..., description="전일 대비 변화율 (%)")
    volume: int = Field(..., description="거래량")
    trading_value: Optional[float] = Field(None, description="거래대금 (원)")


class StockFundamentals(BaseModel):
    """펀더멘털 지표"""
    market_cap: Optional[float] = Field(None, description="시가총액 (원)")
    per: Optional[float] = Field(None, description="주가수익비율 (PER)")
    pbr: Optional[float] = Field(None, description="주가순자산비율 (PBR)")
    eps: Optional[float] = Field(None, description="주당순이익 (EPS)")
    roe: Optional[float] = Field(None, description="자기자본이익률 (%)")
    debt_ratio: Optional[float] = Field(None, description="부채비율 (%)")
    dividend_yield: Optional[float] = Field(None, description="배당수익률 (%)")


class InvestorTrading(BaseModel):
    """투자자별 순매수 데이터"""
    institutional: Optional[float] = Field(None, description="기관 순매수 (원)")
    foreign: Optional[float] = Field(None, description="외국인 순매수 (원)")
    retail: Optional[float] = Field(None, description="개인 순매수 (원)")
    date: Optional[str] = Field(None, description="기준일 (YYYYMMDD)")


class ShortSelling(BaseModel):
    """공매도 데이터"""
    short_ratio: Optional[float] = Field(None, description="공매도 비율 (%)")
    short_balance: Optional[float] = Field(None, description="공매도 잔고 (주)")
    date: Optional[str] = Field(None, description="기준일 (YYYYMMDD)")


class StockPriceResponse(BaseModel):
    """프론트엔드 StockPrice 인터페이스와 1:1 매핑되는 응답 모델 (BUG-002).

    프론트엔드가 기대하는 camelCase 필드명을 사용합니다:
    currentPrice, openPrice, highPrice, lowPrice, closePrice, changePercent
    """
    ticker: str = Field(..., description="종목 코드")
    currentPrice: float = Field(..., description="현재가 (원)")
    openPrice: float = Field(..., description="시가")
    highPrice: float = Field(..., description="고가")
    lowPrice: float = Field(..., description="저가")
    closePrice: float = Field(..., description="전일 종가")
    change: float = Field(..., description="전일 대비 변화량")
    changePercent: float = Field(..., description="전일 대비 변화율 (%)")
    volume: int = Field(..., description="거래량")
    marketCap: Optional[float] = Field(None, description="시가총액 (원)")
    updatedAt: str = Field(..., description="마지막 업데이트 시각 (ISO 8601)")

    @classmethod
    def from_stock_price(
        cls,
        ticker: str,
        price: "StockPrice",
        market_cap: Optional[float] = None,
    ) -> "StockPriceResponse":
        """내부 StockPrice 모델을 프론트엔드 호환 응답으로 변환합니다."""
        return cls(
            ticker=ticker,
            currentPrice=price.current,
            openPrice=price.open,
            highPrice=price.high,
            lowPrice=price.low,
            closePrice=price.prev_close,
            change=price.change,
            changePercent=price.change_pct,
            volume=price.volume,
            marketCap=market_cap,
            updatedAt=datetime.utcnow().isoformat() + "Z",
        )


class StockSummaryResponse(BaseModel):
    """인기 종목 카드에 사용되는 요약 응답 모델 (BUG-001).

    프론트엔드 StockSummary (= Stock + StockPrice) 인터페이스에 맞춥니다.
    """
    ticker: str
    name: str
    market: str
    sector: Optional[str] = None
    currency: str = "KRW"
    currentPrice: float = 0
    openPrice: float = 0
    highPrice: float = 0
    lowPrice: float = 0
    closePrice: float = 0
    change: float = 0
    changePercent: float = 0
    volume: int = 0
    marketCap: Optional[float] = None
    updatedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class StockInfo(BaseModel):
    """종목 기본 정보 (검색 결과 및 상세 조회용)"""
    ticker: str = Field(..., description="종목 코드 (6자리)")
    name: str = Field(..., description="종목명")
    market: str = Field(..., description="시장 구분 (KOSPI/KOSDAQ)")
    sector: Optional[str] = Field(None, description="업종")
    price: Optional[StockPrice] = None
    fundamentals: Optional[StockFundamentals] = None
    investor_trading: Optional[InvestorTrading] = None
    short_selling: Optional[ShortSelling] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ────────────────────────────────────────────────
# AI 분석 결과
# ────────────────────────────────────────────────

class TechnicalAnalysis(BaseModel):
    """기술적 분석 결과"""
    trend: str = Field(..., description="추세 (상승/하락/횡보)")
    support_levels: List[float] = Field(default_factory=list, description="지지선 목록")
    resistance_levels: List[float] = Field(default_factory=list, description="저항선 목록")
    moving_averages: Dict[str, float] = Field(default_factory=dict, description="이동평균 (5일/20일/60일/120일)")
    rsi: Optional[float] = Field(None, description="RSI (14일)")
    volume_trend: str = Field(..., description="거래량 추세")
    summary: str = Field(..., description="기술적 분석 요약")
    signals: List[str] = Field(default_factory=list, description="기술적 신호 목록")


class FundamentalAnalysis(BaseModel):
    """펀더멘털 분석 결과"""
    valuation: str = Field(..., description="밸류에이션 평가 (저평가/적정/고평가)")
    growth_potential: str = Field(..., description="성장 가능성 평가")
    financial_health: str = Field(..., description="재무 건전성 평가")
    peer_comparison: str = Field(..., description="동종업계 비교")
    summary: str = Field(..., description="펀더멘털 분석 요약")
    risks: List[str] = Field(default_factory=list, description="주요 리스크 요소")
    opportunities: List[str] = Field(default_factory=list, description="기회 요소")


class HiddenInsights(BaseModel):
    """숨겨진 인사이트 (비정형 신호)"""
    smart_money_flow: str = Field(..., description="스마트 머니 흐름 분석")
    unusual_activity: List[str] = Field(default_factory=list, description="이상 징후 목록")
    dark_pool_signals: str = Field(..., description="기관/외국인 동향 시그널")
    seasonal_patterns: Optional[str] = Field(None, description="계절적 패턴")
    catalyst_events: List[str] = Field(default_factory=list, description="예상 촉매 이벤트")
    summary: str = Field(..., description="인사이트 요약")


class SentimentAnalysis(BaseModel):
    """센티먼트 분석 결과"""
    overall_sentiment: str = Field(..., description="전반적 시장 심리 (긍정/중립/부정)")
    news_sentiment: str = Field(..., description="뉴스 센티먼트")
    disclosure_sentiment: str = Field(..., description="공시 센티먼트")
    retail_interest: str = Field(..., description="개인투자자 관심도")
    social_buzz: Optional[str] = Field(None, description="소셜미디어 화제도")
    summary: str = Field(..., description="센티먼트 분석 요약")


class AnalysisResult(BaseModel):
    """AI 심층 분석 전체 결과"""
    ticker: str
    name: str
    technical: TechnicalAnalysis
    fundamental: FundamentalAnalysis
    hidden_insights: HiddenInsights
    sentiment: SentimentAnalysis
    overall_summary: str = Field(..., description="종합 분석 요약")
    disclaimer: str = Field(
        default="본 분석은 AI가 생성한 참고 정보이며, 투자 권유가 아닙니다. "
                "투자 결정은 본인의 판단과 책임 하에 이루어져야 합니다.",
        description="법적 면책 문구",
    )
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    cached: bool = Field(default=False, description="캐시에서 반환된 결과 여부")


class TabAnalysisResult(BaseModel):
    """탭별 AI 분석 결과 — 프론트엔드 AnalysisResult 인터페이스에 매핑 (BUG-003).

    프론트엔드가 기대하는 구조:
    { tab, ticker, summary, score?, signals?, details, generatedAt, disclaimer }
    """
    tab: str = Field(..., description="분석 탭 종류 (technical|fundamental|insights|sentiment)")
    ticker: str
    summary: str = Field(..., description="AI 분석 요약")
    score: Optional[int] = Field(None, ge=0, le=100, description="점수 (0-100)")
    details: str = Field(..., description="상세 분석 내용 (마크다운)")
    generatedAt: str = Field(..., description="분석 생성 시각 (ISO 8601)")
    disclaimer: str = Field(..., description="법적 면책 문구")


# ────────────────────────────────────────────────
# 뉴스 / 공시
# ────────────────────────────────────────────────

class NewsItem(BaseModel):
    """뉴스/공시 항목"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="고유 ID (UUID4)")
    title: str
    source: str = Field(..., description="출처 (언론사명 또는 DART)")
    url: Optional[str] = None
    published_at: Optional[str] = Field(None, description="발행 시각 (snake_case, 내부용)")
    publishedAt: Optional[str] = Field(None, description="발행 시각 (camelCase, 프론트엔드용)")
    summary: Optional[str] = None
    sentiment: Optional[str] = Field(None, description="해당 뉴스 센티먼트 (긍정/중립/부정)")
    sentimentScore: Optional[float] = Field(None, ge=-1.0, le=1.0, description="센티먼트 점수 (-1.0 ~ 1.0)")
    is_disclosure: bool = Field(default=False, description="공시 여부")
    isDisclosure: bool = Field(default=False, description="공시 여부 (camelCase, 프론트엔드용)")

    def model_post_init(self, __context) -> None:
        """published_at과 publishedAt, is_disclosure와 isDisclosure를 동기화합니다."""
        # published_at ↔ publishedAt 양방향 동기화
        if self.published_at and not self.publishedAt:
            object.__setattr__(self, 'publishedAt', self.published_at)
        elif self.publishedAt and not self.published_at:
            object.__setattr__(self, 'published_at', self.publishedAt)

        # is_disclosure를 기준으로 isDisclosure 단방향 동기화
        object.__setattr__(self, 'isDisclosure', self.is_disclosure)


class NewsResponse(BaseModel):
    """뉴스/공시 목록 응답"""
    ticker: str
    name: str
    items: List[NewsItem]
    fetched_at: datetime = Field(default_factory=datetime.utcnow)


# ────────────────────────────────────────────────
# 검색 결과
# ────────────────────────────────────────────────

class StockSearchResult(BaseModel):
    """종목 검색 결과 항목"""
    ticker: str
    name: str
    market: str
    current_price: Optional[float] = None
    change_pct: Optional[float] = None


class SearchResponse(BaseModel):
    """검색 응답"""
    query: str
    results: List[StockSearchResult]
    total: int


# ────────────────────────────────────────────────
# 관심종목 (Watchlist)
# ────────────────────────────────────────────────

class WatchlistItem(BaseModel):
    """관심종목 항목"""
    ticker: str
    name: str
    market: str
    added_at: datetime = Field(default_factory=datetime.utcnow)
    current_price: Optional[float] = None
    change_pct: Optional[float] = None
    alert_price: Optional[float] = Field(None, description="알림 설정 가격")


class WatchlistAddRequest(BaseModel):
    """관심종목 추가 요청"""
    ticker: str
    alert_price: Optional[float] = None


class WatchlistResponse(BaseModel):
    """관심종목 목록 응답"""
    items: List[WatchlistItem]
    total: int
