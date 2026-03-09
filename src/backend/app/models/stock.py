"""
StockMind AI — 주식 관련 Pydantic 모델 정의
API 요청/응답 및 내부 데이터 구조 정의
"""
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


# ────────────────────────────────────────────────
# 뉴스 / 공시
# ────────────────────────────────────────────────

class NewsItem(BaseModel):
    """뉴스/공시 항목"""
    title: str
    source: str = Field(..., description="출처 (언론사명 또는 DART)")
    url: Optional[str] = None
    published_at: Optional[str] = None
    summary: Optional[str] = None
    sentiment: Optional[str] = Field(None, description="해당 뉴스 센티먼트")
    is_disclosure: bool = Field(default=False, description="공시 여부")


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
