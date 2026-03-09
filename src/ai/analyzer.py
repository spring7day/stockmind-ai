"""
StockMind AI — src/ai/analyzer.py
Anthropic Claude API 기반 주식 종목 심층 분석 엔진.

StockAnalyzer 클래스는 다음 4가지 분석을 asyncio 기반으로 수행합니다:
  - analyze_technical  : 기술적 분석 (RSI, 이동평균, 지지/저항선)
  - analyze_fundamental: 펀더멘털 분석 (PER/PBR, 밸류에이션, 성장성)
  - analyze_sentiment  : 뉴스 센티먼트 분석
  - generate_insight   : 종합 AI 인사이트 생성
  - analyze_full       : 위 4가지를 병렬 실행 후 통합 결과 반환
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import anthropic

from .models import (
    AIInsight,
    FundamentalAnalysis,
    SentimentAnalysis,
    StockAnalysisResult,
    TechnicalAnalysis,
    DISCLAIMER,
)
from .prompts import (
    get_fundamental_prompt,
    get_insight_prompt,
    get_sentiment_prompt,
    get_technical_prompt,
)

logger = logging.getLogger(__name__)

# Claude API 설정
_DEFAULT_MODEL = "claude-3-5-haiku-20241022"
_MAX_TOKENS = 2048


def _extract_json(raw: str) -> Dict[str, Any]:
    """
    Claude 응답 텍스트에서 JSON 객체를 추출합니다.
    마크다운 코드 블록(```json ... ```)을 처리하고
    순수 JSON 문자열을 파싱합니다.
    """
    text = raw.strip()

    # 마크다운 코드 블록 처리
    if "```" in text:
        # ```json ... ``` 또는 ``` ... ``` 패턴
        parts = text.split("```")
        # 블록 안쪽 내용 선택 (인덱스 1)
        if len(parts) >= 2:
            block = parts[1]
            # 첫 줄이 'json' 같은 언어 식별자인 경우 제거
            lines = block.splitlines()
            if lines and lines[0].strip().lower() in ("json", ""):
                block = "\n".join(lines[1:])
            text = block.strip()

    return json.loads(text)


class StockAnalyzer:
    """
    Claude API를 사용하는 주식 종목 AI 분석기.

    사용 예시:
        analyzer = StockAnalyzer(api_key="sk-ant-...")
        result = await analyzer.analyze_full("005930", market_data)
    """

    def __init__(self, api_key: str, model: Optional[str] = None) -> None:
        """
        Args:
            api_key: Anthropic API 키
            model:   사용할 Claude 모델 ID (기본값: claude-3-5-haiku-20241022)
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model or _DEFAULT_MODEL

    # ------------------------------------------------------------------
    # 내부 헬퍼
    # ------------------------------------------------------------------

    def _call_claude(self, prompt: str) -> str:
        """
        동기 방식으로 Claude API를 호출하고 응답 텍스트를 반환합니다.
        asyncio.get_running_loop().run_in_executor 를 통해 비동기에서 호출됩니다.
        """
        message = self.client.messages.create(
            model=self.model,
            max_tokens=_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    async def _async_call_claude(self, prompt: str) -> str:
        """
        블로킹 API 호출을 스레드 풀에서 실행해 이벤트 루프를 차단하지 않습니다.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._call_claude, prompt)

    # ------------------------------------------------------------------
    # 폴백 반환값 — API 오류 시 서비스 중단 방지
    # ------------------------------------------------------------------

    @staticmethod
    def _fallback_technical(ticker: str) -> TechnicalAnalysis:
        return TechnicalAnalysis(
            trend="횡보",
            volume_trend="보합",
            summary=f"[{ticker}] 기술적 분석 데이터를 일시적으로 가져올 수 없습니다.",
            signals=[],
        )

    @staticmethod
    def _fallback_fundamental(ticker: str) -> FundamentalAnalysis:
        return FundamentalAnalysis(
            valuation="적정",
            growth_potential="보통",
            financial_health="양호",
            peer_comparison="동종업계 비교 데이터를 일시적으로 가져올 수 없습니다.",
            summary=f"[{ticker}] 펀더멘털 분석 데이터를 일시적으로 가져올 수 없습니다.",
            risks=[],
            opportunities=[],
        )

    @staticmethod
    def _fallback_sentiment(ticker: str) -> SentimentAnalysis:
        return SentimentAnalysis(
            overall_sentiment="중립",
            news_sentiment="중립",
            disclosure_sentiment="중립",
            retail_interest="보통",
            social_buzz=None,
            summary=f"[{ticker}] 센티먼트 분석 데이터를 일시적으로 가져올 수 없습니다.",
        )

    @staticmethod
    def _fallback_insight(ticker: str) -> AIInsight:
        return AIInsight(
            summary=f"[{ticker}] AI 인사이트 데이터를 일시적으로 가져올 수 없습니다.",
            key_points=[],
            risk_warnings=[],
            smart_money_flow="스마트 머니 흐름 데이터를 일시적으로 가져올 수 없습니다.",
            catalyst_events=[],
        )

    # ------------------------------------------------------------------
    # 공개 분석 메서드
    # ------------------------------------------------------------------

    async def analyze_technical(
        self, ticker: str, price_data: Dict[str, Any]
    ) -> TechnicalAnalysis:
        """
        기술적 분석을 수행합니다.

        Args:
            ticker:     종목 코드
            price_data: 주가 및 기술 지표 딕셔너리
                        (current_price, open, high, low, prev_close, change_pct,
                         volume, moving_averages, rsi, macd 등)

        Returns:
            TechnicalAnalysis 인스턴스
        """
        prompt = get_technical_prompt(ticker, price_data)
        try:
            raw = await self._async_call_claude(prompt)
            data = _extract_json(raw)
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
        except json.JSONDecodeError as e:
            logger.warning(
                "[%s] 기술적 분석 JSON 파싱 실패, 폴백 반환: %s", ticker, e
            )
            return self._fallback_technical(ticker)
        except Exception as e:
            logger.error("[%s] 기술적 분석 오류: %s", ticker, e)
            return self._fallback_technical(ticker)

    async def analyze_fundamental(
        self, ticker: str, financial_data: Dict[str, Any]
    ) -> FundamentalAnalysis:
        """
        펀더멘털 분석을 수행합니다.

        Args:
            ticker:         종목 코드
            financial_data: 재무/밸류에이션 딕셔너리
                            (name, market, market_cap, per, pbr, eps, roe,
                             debt_ratio, dividend_yield, sector 등)

        Returns:
            FundamentalAnalysis 인스턴스
        """
        prompt = get_fundamental_prompt(ticker, financial_data)
        try:
            raw = await self._async_call_claude(prompt)
            data = _extract_json(raw)
            return FundamentalAnalysis(
                valuation=data.get("valuation", "적정"),
                growth_potential=data.get("growth_potential", "보통"),
                financial_health=data.get("financial_health", "양호"),
                peer_comparison=data.get("peer_comparison", ""),
                summary=data.get("summary", ""),
                risks=data.get("risks", []),
                opportunities=data.get("opportunities", []),
            )
        except json.JSONDecodeError as e:
            logger.warning(
                "[%s] 펀더멘털 분석 JSON 파싱 실패, 폴백 반환: %s", ticker, e
            )
            return self._fallback_fundamental(ticker)
        except Exception as e:
            logger.error("[%s] 펀더멘털 분석 오류: %s", ticker, e)
            return self._fallback_fundamental(ticker)

    async def analyze_sentiment(
        self, ticker: str, news: List[Dict[str, Any]]
    ) -> SentimentAnalysis:
        """
        뉴스/공시 센티먼트 분석을 수행합니다.

        Args:
            ticker: 종목 코드
            news:   뉴스/공시 항목 딕셔너리 목록
                    각 항목 권장 키: title, source, published_at, summary, is_disclosure

        Returns:
            SentimentAnalysis 인스턴스
        """
        prompt = get_sentiment_prompt(ticker, news)
        try:
            raw = await self._async_call_claude(prompt)
            data = _extract_json(raw)
            return SentimentAnalysis(
                overall_sentiment=data.get("overall_sentiment", "중립"),
                news_sentiment=data.get("news_sentiment", "중립"),
                disclosure_sentiment=data.get("disclosure_sentiment", "중립"),
                retail_interest=data.get("retail_interest", "보통"),
                social_buzz=data.get("social_buzz"),
                summary=data.get("summary", ""),
            )
        except json.JSONDecodeError as e:
            logger.warning(
                "[%s] 센티먼트 분석 JSON 파싱 실패, 폴백 반환: %s", ticker, e
            )
            return self._fallback_sentiment(ticker)
        except Exception as e:
            logger.error("[%s] 센티먼트 분석 오류: %s", ticker, e)
            return self._fallback_sentiment(ticker)

    async def generate_insight(
        self, ticker: str, all_data: Dict[str, Any]
    ) -> AIInsight:
        """
        기술적/펀더멘털/센티먼트 분석 결과를 종합한 AI 인사이트를 생성합니다.

        Args:
            ticker:   종목 코드
            all_data: 전체 분석 데이터 딕셔너리
                      권장 키: technical, fundamental, sentiment, price_info, news_summary

        Returns:
            AIInsight 인스턴스
        """
        prompt = get_insight_prompt(ticker, all_data)
        try:
            raw = await self._async_call_claude(prompt)
            data = _extract_json(raw)
            return AIInsight(
                summary=data.get("summary", ""),
                key_points=data.get("key_points", []),
                risk_warnings=data.get("risk_warnings", []),
                smart_money_flow=data.get("smart_money_flow", ""),
                catalyst_events=data.get("catalyst_events", []),
            )
        except json.JSONDecodeError as e:
            logger.warning(
                "[%s] AI 인사이트 JSON 파싱 실패, 폴백 반환: %s", ticker, e
            )
            return self._fallback_insight(ticker)
        except Exception as e:
            logger.error("[%s] AI 인사이트 오류: %s", ticker, e)
            return self._fallback_insight(ticker)

    async def analyze_full(
        self, ticker: str, market_data: Dict[str, Any]
    ) -> StockAnalysisResult:
        """
        4가지 분석(기술적/펀더멘털/센티먼트/인사이트)을 병렬로 실행하고
        통합 결과를 반환합니다.

        각 분석이 실패하더라도 폴백 값을 사용해 전체 서비스는 계속 동작합니다.

        Args:
            ticker:      종목 코드
            market_data: 시장 데이터 딕셔너리.
                         권장 구조:
                           {
                             "price": {...},       # 주가 정보
                             "fundamentals": {...}, # 재무 지표
                             "news": [...],         # 뉴스/공시 목록
                             "investor_trading": {...},
                             "short_selling": {...},
                           }

        Returns:
            StockAnalysisResult 인스턴스
        """
        price_data: Dict[str, Any] = market_data.get("price", {})
        fundamental_data: Dict[str, Any] = {
            **market_data.get("fundamentals", {}),
            "investor_trading": market_data.get("investor_trading", {}),
            "short_selling": market_data.get("short_selling", {}),
        }
        news_list: List[Dict[str, Any]] = market_data.get("news", [])

        # 기술적/펀더멘털/센티먼트 분석을 병렬로 실행
        technical_task = self.analyze_technical(ticker, price_data)
        fundamental_task = self.analyze_fundamental(ticker, fundamental_data)
        sentiment_task = self.analyze_sentiment(ticker, news_list)

        technical, fundamental, sentiment = await asyncio.gather(
            technical_task,
            fundamental_task,
            sentiment_task,
            return_exceptions=True,
        )

        # 예외 발생 시 폴백으로 교체
        if isinstance(technical, Exception):
            logger.error("[%s] 기술적 분석 태스크 예외: %s", ticker, technical)
            technical = self._fallback_technical(ticker)
        if isinstance(fundamental, Exception):
            logger.error("[%s] 펀더멘털 분석 태스크 예외: %s", ticker, fundamental)
            fundamental = self._fallback_fundamental(ticker)
        if isinstance(sentiment, Exception):
            logger.error("[%s] 센티먼트 분석 태스크 예외: %s", ticker, sentiment)
            sentiment = self._fallback_sentiment(ticker)

        # 종합 인사이트 생성 (앞의 3가지 결과 활용)
        combined_data: Dict[str, Any] = {
            "ticker": ticker,
            "technical": technical.model_dump(),
            "fundamental": fundamental.model_dump(),
            "sentiment": sentiment.model_dump(),
            "price_info": price_data,
            "news_summary": (
                f"뉴스 {len(news_list)}건 분석 완료" if news_list else "뉴스 없음"
            ),
        }

        insight = await self.generate_insight(ticker, combined_data)
        if isinstance(insight, Exception):
            logger.error("[%s] AI 인사이트 태스크 예외: %s", ticker, insight)
            insight = self._fallback_insight(ticker)

        # 전체 종합 요약 생성
        overall_summary = (
            f"[{ticker}] 현재 {technical.trend} 추세이며, "
            f"펀더멘털 관점에서 {fundamental.valuation} 상태입니다. "
            f"시장 심리는 전반적으로 {sentiment.overall_sentiment}으로 평가됩니다. "
            f"{DISCLAIMER}"
        )

        return StockAnalysisResult(
            ticker=ticker,
            technical=technical,
            fundamental=fundamental,
            sentiment=sentiment,
            insight=insight,
            overall_summary=overall_summary,
            disclaimer=DISCLAIMER,
            analyzed_at=datetime.utcnow(),
            cached=False,
        )
