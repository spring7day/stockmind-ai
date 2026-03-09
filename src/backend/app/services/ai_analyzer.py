"""
StockMind AI — Anthropic Claude API 기반 주식 분석 서비스
기술적분석 / 펀더멘털 / 숨겨진인사이트 / 센티먼트 4가지 분석을 제공합니다.
"""
import json
import logging
from typing import Dict, List, Optional

import anthropic

from app.config import settings
from app.models.stock import (
    AnalysisResult,
    FundamentalAnalysis,
    HiddenInsights,
    NewsItem,
    SentimentAnalysis,
    StockInfo,
    TechnicalAnalysis,
)

logger = logging.getLogger(__name__)

# 면책 문구 (모든 분석 결과에 포함)
DISCLAIMER = (
    "본 분석은 AI가 생성한 참고 정보이며, 투자 권유가 아닙니다. "
    "투자 결정은 본인의 판단과 책임 하에 이루어져야 합니다. "
    "과거 성과가 미래 수익을 보장하지 않습니다."
)

# Claude 모델 설정
CLAUDE_MODEL = "claude-opus-4-6"
MAX_TOKENS = 2048


def _get_client() -> anthropic.AsyncAnthropic:
    """Anthropic 비동기 클라이언트를 반환합니다."""
    if not settings.ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY가 설정되지 않았습니다.")
    return anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)


def _format_stock_context(stock_info: StockInfo) -> str:
    """StockInfo를 Claude에게 전달할 텍스트 컨텍스트로 변환합니다."""
    lines = [
        f"종목명: {stock_info.name} ({stock_info.ticker})",
        f"시장: {stock_info.market}",
    ]

    if stock_info.price:
        p = stock_info.price
        lines += [
            f"\n[주가 정보]",
            f"현재가: {p.current:,.0f}원",
            f"시가: {p.open:,.0f}원 / 고가: {p.high:,.0f}원 / 저가: {p.low:,.0f}원",
            f"전일 종가: {p.prev_close:,.0f}원",
            f"등락률: {p.change_pct:+.2f}%",
            f"거래량: {p.volume:,}주",
        ]

    if stock_info.fundamentals:
        f = stock_info.fundamentals
        lines += ["\n[펀더멘털]"]
        if f.market_cap:
            lines.append(f"시가총액: {f.market_cap / 1e8:,.0f}억원")
        if f.per is not None:
            lines.append(f"PER: {f.per:.2f}배")
        if f.pbr is not None:
            lines.append(f"PBR: {f.pbr:.2f}배")
        if f.eps is not None:
            lines.append(f"EPS: {f.eps:,.0f}원")
        if f.dividend_yield is not None:
            lines.append(f"배당수익률: {f.dividend_yield:.2f}%")

    if stock_info.investor_trading:
        it = stock_info.investor_trading
        lines += ["\n[투자자 동향]"]
        if it.institutional is not None:
            lines.append(f"기관 순매수: {it.institutional / 1e8:+,.1f}억원")
        if it.foreign is not None:
            lines.append(f"외국인 순매수: {it.foreign / 1e8:+,.1f}억원")
        if it.retail is not None:
            lines.append(f"개인 순매수: {it.retail / 1e8:+,.1f}억원")

    if stock_info.short_selling:
        ss = stock_info.short_selling
        lines += ["\n[공매도]"]
        if ss.short_ratio is not None:
            lines.append(f"공매도 비율: {ss.short_ratio:.2f}%")

    return "\n".join(lines)


async def analyze_technical(stock_info: StockInfo) -> TechnicalAnalysis:
    """
    기술적 분석을 수행합니다.
    주가 패턴, 이동평균, 지지/저항선, 거래량 추세를 분석합니다.
    """
    context = _format_stock_context(stock_info)

    prompt = f"""
당신은 한국 주식 시장의 전문 기술적 분석가입니다.
다음 주식 데이터를 분석하여 기술적 분석 결과를 JSON 형식으로 반환해주세요.

{context}

다음 JSON 스키마에 맞게 응답하세요 (다른 텍스트 없이 JSON만 반환):
{{
  "trend": "상승|하락|횡보 중 하나",
  "support_levels": [지지선 가격 숫자 목록, 최대 3개],
  "resistance_levels": [저항선 가격 숫자 목록, 최대 3개],
  "moving_averages": {{"5일": 숫자, "20일": 숫자, "60일": 숫자}},
  "rsi": RSI 수치 또는 null,
  "volume_trend": "증가|감소|보합 중 하나",
  "summary": "기술적 분석 2-3문장 요약",
  "signals": ["신호1", "신호2", ...] 최대 5개
}}
"""

    try:
        client = _get_client()
        message = await client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()
        # JSON 블록 추출
        if "```" in raw:
            raw = raw.split("```")[1].lstrip("json").strip()
        data = json.loads(raw)

        return TechnicalAnalysis(
            trend=data.get("trend", "횡보"),
            support_levels=data.get("support_levels", []),
            resistance_levels=data.get("resistance_levels", []),
            moving_averages=data.get("moving_averages", {}),
            rsi=data.get("rsi"),
            volume_trend=data.get("volume_trend", "보합"),
            summary=data.get("summary", ""),
            signals=data.get("signals", []),
        )
    except Exception as e:
        logger.error(f"[{stock_info.ticker}] 기술적 분석 실패: {e}")
        return _fallback_technical(stock_info)


async def analyze_fundamental(stock_info: StockInfo) -> FundamentalAnalysis:
    """
    펀더멘털 분석을 수행합니다.
    밸류에이션, 성장성, 재무 건전성, 동종업계 비교를 분석합니다.
    """
    context = _format_stock_context(stock_info)

    prompt = f"""
당신은 한국 주식 시장의 전문 가치 투자 분석가입니다.
다음 주식 데이터를 분석하여 펀더멘털 분석 결과를 JSON 형식으로 반환해주세요.

{context}

다음 JSON 스키마에 맞게 응답하세요 (다른 텍스트 없이 JSON만 반환):
{{
  "valuation": "저평가|적정|고평가 중 하나",
  "growth_potential": "높음|보통|낮음 중 하나",
  "financial_health": "우수|양호|주의|위험 중 하나",
  "peer_comparison": "동종업계와의 비교 1-2문장",
  "summary": "펀더멘털 분석 2-3문장 요약",
  "risks": ["리스크1", "리스크2", ...] 최대 4개,
  "opportunities": ["기회1", "기회2", ...] 최대 4개
}}
"""

    try:
        client = _get_client()
        message = await client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()
        if "```" in raw:
            raw = raw.split("```")[1].lstrip("json").strip()
        data = json.loads(raw)

        return FundamentalAnalysis(
            valuation=data.get("valuation", "적정"),
            growth_potential=data.get("growth_potential", "보통"),
            financial_health=data.get("financial_health", "양호"),
            peer_comparison=data.get("peer_comparison", ""),
            summary=data.get("summary", ""),
            risks=data.get("risks", []),
            opportunities=data.get("opportunities", []),
        )
    except Exception as e:
        logger.error(f"[{stock_info.ticker}] 펀더멘털 분석 실패: {e}")
        return _fallback_fundamental()


async def analyze_hidden_insights(
    stock_info: StockInfo, news_items: Optional[List[NewsItem]] = None
) -> HiddenInsights:
    """
    숨겨진 인사이트 분석을 수행합니다.
    스마트 머니 흐름, 이상 징후, 기관/외국인 동향을 분석합니다.
    """
    context = _format_stock_context(stock_info)

    # 뉴스/공시 컨텍스트 추가
    news_context = ""
    if news_items:
        news_titles = [f"- {item.title} ({item.source})" for item in news_items[:5]]
        news_context = "\n[최근 뉴스/공시]\n" + "\n".join(news_titles)

    prompt = f"""
당신은 한국 주식 시장의 퀀트 및 기관 투자 전문가입니다.
다음 데이터를 분석하여 일반 투자자가 놓치기 쉬운 숨겨진 인사이트를 JSON 형식으로 반환해주세요.

{context}{news_context}

다음 JSON 스키마에 맞게 응답하세요 (다른 텍스트 없이 JSON만 반환):
{{
  "smart_money_flow": "스마트 머니(기관/외국인) 흐름 분석 1-2문장",
  "unusual_activity": ["이상 징후1", "이상 징후2", ...] 최대 4개,
  "dark_pool_signals": "기관/외국인 숨겨진 동향 시그널 1-2문장",
  "seasonal_patterns": "계절적 패턴 설명 또는 null",
  "catalyst_events": ["예상 촉매 이벤트1", "이벤트2", ...] 최대 4개,
  "summary": "숨겨진 인사이트 종합 요약 2-3문장"
}}
"""

    try:
        client = _get_client()
        message = await client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()
        if "```" in raw:
            raw = raw.split("```")[1].lstrip("json").strip()
        data = json.loads(raw)

        return HiddenInsights(
            smart_money_flow=data.get("smart_money_flow", ""),
            unusual_activity=data.get("unusual_activity", []),
            dark_pool_signals=data.get("dark_pool_signals", ""),
            seasonal_patterns=data.get("seasonal_patterns"),
            catalyst_events=data.get("catalyst_events", []),
            summary=data.get("summary", ""),
        )
    except Exception as e:
        logger.error(f"[{stock_info.ticker}] 숨겨진 인사이트 분석 실패: {e}")
        return _fallback_hidden_insights()


async def analyze_sentiment(
    stock_info: StockInfo, news_items: Optional[List[NewsItem]] = None
) -> SentimentAnalysis:
    """
    센티먼트 분석을 수행합니다.
    뉴스, 공시, 투자자 심리를 종합적으로 분석합니다.
    """
    context = _format_stock_context(stock_info)

    news_context = ""
    if news_items:
        news_titles = [f"- [{item.source}] {item.title}" for item in news_items[:8]]
        news_context = "\n[최근 뉴스/공시]\n" + "\n".join(news_titles)

    prompt = f"""
당신은 한국 주식 시장의 심리 분석 전문가입니다.
다음 데이터를 바탕으로 시장 심리 분석 결과를 JSON 형식으로 반환해주세요.

{context}{news_context}

다음 JSON 스키마에 맞게 응답하세요 (다른 텍스트 없이 JSON만 반환):
{{
  "overall_sentiment": "긍정|중립|부정 중 하나",
  "news_sentiment": "긍정|중립|부정 중 하나",
  "disclosure_sentiment": "긍정|중립|부정 중 하나 (공시가 없으면 중립)",
  "retail_interest": "높음|보통|낮음 중 하나",
  "social_buzz": "소셜 화제도 설명 또는 null",
  "summary": "센티먼트 종합 분석 2-3문장"
}}
"""

    try:
        client = _get_client()
        message = await client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()
        if "```" in raw:
            raw = raw.split("```")[1].lstrip("json").strip()
        data = json.loads(raw)

        return SentimentAnalysis(
            overall_sentiment=data.get("overall_sentiment", "중립"),
            news_sentiment=data.get("news_sentiment", "중립"),
            disclosure_sentiment=data.get("disclosure_sentiment", "중립"),
            retail_interest=data.get("retail_interest", "보통"),
            social_buzz=data.get("social_buzz"),
            summary=data.get("summary", ""),
        )
    except Exception as e:
        logger.error(f"[{stock_info.ticker}] 센티먼트 분석 실패: {e}")
        return _fallback_sentiment()


async def run_full_analysis(
    stock_info: StockInfo, news_items: Optional[List[NewsItem]] = None
) -> AnalysisResult:
    """
    4가지 분석을 병렬로 실행하고 종합 결과를 반환합니다.
    각 분석 실패 시 폴백 결과를 사용합니다.
    """
    import asyncio

    # 4가지 분석 병렬 실행
    technical, fundamental, hidden, sentiment = await asyncio.gather(
        analyze_technical(stock_info),
        analyze_fundamental(stock_info),
        analyze_hidden_insights(stock_info, news_items),
        analyze_sentiment(stock_info, news_items),
        return_exceptions=True,
    )

    # 예외 처리
    if isinstance(technical, Exception):
        technical = _fallback_technical(stock_info)
    if isinstance(fundamental, Exception):
        fundamental = _fallback_fundamental()
    if isinstance(hidden, Exception):
        hidden = _fallback_hidden_insights()
    if isinstance(sentiment, Exception):
        sentiment = _fallback_sentiment()

    # 종합 요약 생성
    overall_summary = _generate_overall_summary(stock_info, technical, fundamental, sentiment)

    return AnalysisResult(
        ticker=stock_info.ticker,
        name=stock_info.name,
        technical=technical,
        fundamental=fundamental,
        hidden_insights=hidden,
        sentiment=sentiment,
        overall_summary=overall_summary,
        disclaimer=DISCLAIMER,
    )


def _generate_overall_summary(
    stock_info: StockInfo,
    technical: TechnicalAnalysis,
    fundamental: FundamentalAnalysis,
    sentiment: SentimentAnalysis,
) -> str:
    """각 분석 결과를 종합한 한 줄 요약을 생성합니다."""
    name = stock_info.name
    trend = technical.trend
    valuation = fundamental.valuation
    sent = sentiment.overall_sentiment

    return (
        f"{name}은(는) 현재 {trend} 추세이며, "
        f"펀더멘털 관점에서 {valuation} 상태입니다. "
        f"시장 심리는 전반적으로 {sent}으로 평가됩니다. "
        f"{DISCLAIMER}"
    )


# ────────────────────────────────────────────────
# 폴백 함수 — API 오류 시 기본값 반환
# ────────────────────────────────────────────────

def _fallback_technical(stock_info: StockInfo) -> TechnicalAnalysis:
    return TechnicalAnalysis(
        trend="횡보",
        volume_trend="보합",
        summary=f"{stock_info.name}의 기술적 분석 데이터를 일시적으로 가져올 수 없습니다.",
        signals=[],
    )


def _fallback_fundamental() -> FundamentalAnalysis:
    return FundamentalAnalysis(
        valuation="적정",
        growth_potential="보통",
        financial_health="양호",
        peer_comparison="동종업계 비교 데이터를 일시적으로 가져올 수 없습니다.",
        summary="펀더멘털 분석 데이터를 일시적으로 가져올 수 없습니다.",
    )


def _fallback_hidden_insights() -> HiddenInsights:
    return HiddenInsights(
        smart_money_flow="스마트 머니 흐름 데이터를 일시적으로 가져올 수 없습니다.",
        dark_pool_signals="기관/외국인 동향 데이터를 일시적으로 가져올 수 없습니다.",
        summary="숨겨진 인사이트 분석 데이터를 일시적으로 가져올 수 없습니다.",
    )


def _fallback_sentiment() -> SentimentAnalysis:
    return SentimentAnalysis(
        overall_sentiment="중립",
        news_sentiment="중립",
        disclosure_sentiment="중립",
        retail_interest="보통",
        summary="센티먼트 분석 데이터를 일시적으로 가져올 수 없습니다.",
    )
