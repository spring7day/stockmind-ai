"""
StockMind AI — src/ai/models.py
AI 분석 엔진 전용 Pydantic v2 모델 정의.
백엔드의 src/backend/app/models/stock.py 모델과 호환됩니다.
"""
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

# 면책 문구 (공통)
DISCLAIMER = (
    "본 분석은 AI가 생성한 참고 정보이며, 투자 권유가 아닙니다. "
    "투자 결정은 본인의 판단과 책임 하에 이루어져야 합니다. "
    "과거 성과가 미래 수익을 보장하지 않습니다."
)


class TechnicalAnalysis(BaseModel):
    """기술적 분석 결과 — 백엔드 TechnicalAnalysis 모델과 동일한 필드 구조"""

    trend: str = Field(..., description="추세 (상승/하락/횡보)")
    support_levels: List[float] = Field(
        default_factory=list, description="지지선 목록 (최대 3개)"
    )
    resistance_levels: List[float] = Field(
        default_factory=list, description="저항선 목록 (최대 3개)"
    )
    moving_averages: Dict[str, float] = Field(
        default_factory=dict, description="이동평균선 값 (5일/20일/60일/120일)"
    )
    rsi: Optional[float] = Field(None, description="RSI 지수 (14일 기준)")
    volume_trend: str = Field(..., description="거래량 추세 (증가/감소/보합)")
    summary: str = Field(..., description="기술적 분석 요약 (2~3문장)")
    signals: List[str] = Field(
        default_factory=list, description="기술적 시그널 목록 (최대 5개)"
    )


class FundamentalAnalysis(BaseModel):
    """펀더멘털 분석 결과 — 백엔드 FundamentalAnalysis 모델과 동일한 필드 구조"""

    valuation: str = Field(..., description="밸류에이션 평가 (저평가/적정/고평가)")
    growth_potential: str = Field(..., description="성장 가능성 (높음/보통/낮음)")
    financial_health: str = Field(
        ..., description="재무 건전성 (우수/양호/주의/위험)"
    )
    peer_comparison: str = Field(..., description="동종업계 비교 분석 (1~2문장)")
    summary: str = Field(..., description="펀더멘털 분석 요약 (2~3문장)")
    risks: List[str] = Field(default_factory=list, description="주요 리스크 목록")
    opportunities: List[str] = Field(
        default_factory=list, description="기회 요소 목록"
    )


class SentimentAnalysis(BaseModel):
    """센티먼트 분석 결과 — 백엔드 SentimentAnalysis 모델과 동일한 필드 구조"""

    overall_sentiment: str = Field(
        ..., description="전반적 시장 심리 (긍정/중립/부정)"
    )
    news_sentiment: str = Field(..., description="뉴스 센티먼트 (긍정/중립/부정)")
    disclosure_sentiment: str = Field(
        ..., description="공시 센티먼트 (긍정/중립/부정)"
    )
    retail_interest: str = Field(..., description="개인투자자 관심도 (높음/보통/낮음)")
    social_buzz: Optional[str] = Field(None, description="소셜미디어 화제도 설명")
    summary: str = Field(..., description="센티먼트 종합 분석 요약 (2~3문장)")


class AIInsight(BaseModel):
    """종합 AI 인사이트 — 세 가지 핵심 포인트와 리스크 경고 포함"""

    summary: str = Field(..., description="종합 AI 인사이트 요약 (3~4문장)")
    key_points: List[str] = Field(
        default_factory=list,
        description="핵심 포인트 3가지 (상승/하락 모멘텀, 주목할 변화 등)",
    )
    risk_warnings: List[str] = Field(
        default_factory=list, description="리스크 경고 항목 목록"
    )
    smart_money_flow: str = Field(
        ..., description="스마트 머니(기관/외국인) 흐름 분석"
    )
    catalyst_events: List[str] = Field(
        default_factory=list, description="향후 예상 촉매 이벤트 목록"
    )


class StockAnalysisResult(BaseModel):
    """AI 전체 분석 결과 — 4가지 분석 + 메타 정보"""

    ticker: str = Field(..., description="종목 코드")
    technical: TechnicalAnalysis
    fundamental: FundamentalAnalysis
    sentiment: SentimentAnalysis
    insight: AIInsight
    overall_summary: str = Field(..., description="전체 종합 요약")
    disclaimer: str = Field(
        default=DISCLAIMER,
        description="법적 면책 문구",
    )
    analyzed_at: datetime = Field(
        default_factory=datetime.utcnow, description="분석 수행 시각 (UTC)"
    )
    cached: bool = Field(default=False, description="캐시에서 반환된 결과 여부")
