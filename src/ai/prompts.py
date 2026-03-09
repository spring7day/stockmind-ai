"""
StockMind AI — src/ai/prompts.py
Claude API 호출용 프롬프트 템플릿 함수 모음.

주의사항:
- 매수/매도 표현 금지: "상승 모멘텀", "하락 압력" 등의 중립적 표현 사용
- 모든 프롬프트 끝에 면책 문구 포함
- JSON만 반환하도록 지시 (파싱 용이성)
"""

import json
from typing import Any, Dict, List

# 공통 면책 문구
_DISCLAIMER_LINE = (
    "이 분석은 투자 참고용이며 투자 권유가 아닙니다. "
    "투자 결정은 본인의 판단과 책임 하에 이루어져야 합니다."
)

# 공통 표현 금지 지침
_EXPRESSION_GUIDE = (
    "주의: '매수', '매도', '사라', '팔아라' 같은 직접적 투자 지시 표현을 절대 사용하지 마세요. "
    "대신 '상승 모멘텀', '하락 압력', '긍정적 흐름', '부정적 신호', "
    "'주목할 변화', '하락 리스크' 등의 중립적 분석 표현을 사용하세요."
)


def get_technical_prompt(ticker: str, data: Dict[str, Any]) -> str:
    """
    기술적 분석용 Claude 프롬프트를 생성합니다.

    Args:
        ticker: 종목 코드 (예: '005930')
        data: 주가 및 기술 지표 데이터 딕셔너리.
              권장 키: current_price, open, high, low, prev_close, change_pct,
                       volume, moving_averages (dict), rsi, macd

    Returns:
        Claude API 호출용 완성된 프롬프트 문자열
    """
    data_json = json.dumps(data, ensure_ascii=False, indent=2)

    return f"""당신은 한국 주식 시장의 전문 기술적 분석가입니다.
종목 코드 [{ticker}]의 다음 데이터를 분석하여 기술적 분석 결과를 JSON 형식으로 반환해주세요.

[입력 데이터]
{data_json}

{_EXPRESSION_GUIDE}

다음 JSON 스키마에 정확히 맞게 응답하세요. 다른 텍스트나 설명 없이 순수한 JSON만 반환하세요:
{{
  "trend": "상승 또는 하락 또는 횡보",
  "support_levels": [지지선 가격 숫자 목록, 최대 3개],
  "resistance_levels": [저항선 가격 숫자 목록, 최대 3개],
  "moving_averages": {{"5일": 숫자, "20일": 숫자, "60일": 숫자}},
  "rsi": RSI 수치(숫자) 또는 null,
  "volume_trend": "증가 또는 감소 또는 보합",
  "summary": "기술적 분석 2~3문장 요약 (매수/매도 표현 사용 금지)",
  "signals": ["시그널1", "시그널2"] 최대 5개
}}

참고: {_DISCLAIMER_LINE}"""


def get_fundamental_prompt(ticker: str, data: Dict[str, Any]) -> str:
    """
    펀더멘털 분석용 Claude 프롬프트를 생성합니다.

    Args:
        ticker: 종목 코드 (예: '005930')
        data: 재무 및 밸류에이션 데이터 딕셔너리.
              권장 키: name, market, market_cap, per, pbr, eps, roe,
                       debt_ratio, dividend_yield, sector

    Returns:
        Claude API 호출용 완성된 프롬프트 문자열
    """
    data_json = json.dumps(data, ensure_ascii=False, indent=2)

    return f"""당신은 한국 주식 시장의 전문 가치 투자 분석가입니다.
종목 코드 [{ticker}]의 다음 재무 데이터를 분석하여 펀더멘털 분석 결과를 JSON 형식으로 반환해주세요.

[입력 데이터]
{data_json}

{_EXPRESSION_GUIDE}

다음 JSON 스키마에 정확히 맞게 응답하세요. 다른 텍스트나 설명 없이 순수한 JSON만 반환하세요:
{{
  "valuation": "저평가 또는 적정 또는 고평가",
  "growth_potential": "높음 또는 보통 또는 낮음",
  "financial_health": "우수 또는 양호 또는 주의 또는 위험",
  "peer_comparison": "동종업계와의 비교 분석 1~2문장",
  "summary": "펀더멘털 분석 2~3문장 요약 (매수/매도 표현 사용 금지)",
  "risks": ["리스크1", "리스크2"] 최대 4개,
  "opportunities": ["기회1", "기회2"] 최대 4개
}}

참고: {_DISCLAIMER_LINE}"""


def get_sentiment_prompt(ticker: str, news_items: List[Dict[str, Any]]) -> str:
    """
    뉴스 센티먼트 분석용 Claude 프롬프트를 생성합니다.

    Args:
        ticker: 종목 코드 (예: '005930')
        news_items: 뉴스/공시 항목 목록.
                    각 항목 권장 키: title, source, published_at, summary, is_disclosure

    Returns:
        Claude API 호출용 완성된 프롬프트 문자열
    """
    # 최대 10개 뉴스만 포함 (토큰 절약)
    truncated = news_items[:10]
    news_json = json.dumps(truncated, ensure_ascii=False, indent=2)

    return f"""당신은 한국 주식 시장의 뉴스 및 심리 분석 전문가입니다.
종목 코드 [{ticker}]의 최근 뉴스와 공시를 분석하여 센티먼트 분석 결과를 JSON 형식으로 반환해주세요.

[뉴스 및 공시 데이터]
{news_json}

{_EXPRESSION_GUIDE}

다음 JSON 스키마에 정확히 맞게 응답하세요. 다른 텍스트나 설명 없이 순수한 JSON만 반환하세요:
{{
  "overall_sentiment": "긍정 또는 중립 또는 부정",
  "news_sentiment": "긍정 또는 중립 또는 부정",
  "disclosure_sentiment": "긍정 또는 중립 또는 부정 (공시가 없으면 중립)",
  "retail_interest": "높음 또는 보통 또는 낮음",
  "social_buzz": "소셜 화제도 설명 1문장 또는 null",
  "summary": "센티먼트 종합 분석 2~3문장 (매수/매도 표현 사용 금지)"
}}

참고: {_DISCLAIMER_LINE}"""


def get_insight_prompt(ticker: str, all_data: Dict[str, Any]) -> str:
    """
    종합 AI 인사이트 생성용 Claude 프롬프트를 생성합니다.
    기술적 분석, 펀더멘털 분석, 센티먼트 분석 결과를 모두 받아 통합 인사이트를 도출합니다.

    Args:
        ticker: 종목 코드 (예: '005930')
        all_data: 전체 분석 데이터 딕셔너리.
                  권장 키: technical (TechnicalAnalysis dict),
                           fundamental (FundamentalAnalysis dict),
                           sentiment (SentimentAnalysis dict),
                           price_info (dict), news_summary (str)

    Returns:
        Claude API 호출용 완성된 프롬프트 문자열
    """
    data_json = json.dumps(all_data, ensure_ascii=False, indent=2)

    return f"""당신은 한국 주식 시장의 시니어 리서치 애널리스트입니다.
종목 코드 [{ticker}]에 대한 기술적 분석, 펀더멘털 분석, 센티먼트 분석 결과를 종합하여
일반 투자자가 이해하기 쉬운 핵심 인사이트를 JSON 형식으로 반환해주세요.

[종합 분석 데이터]
{data_json}

{_EXPRESSION_GUIDE}

다음 JSON 스키마에 정확히 맞게 응답하세요. 다른 텍스트나 설명 없이 순수한 JSON만 반환하세요:
{{
  "summary": "종합 AI 인사이트 요약 3~4문장 (매수/매도 표현 사용 금지)",
  "key_points": [
    "핵심 포인트 1 (예: 상승 모멘텀 관련)",
    "핵심 포인트 2 (예: 펀더멘털 관련)",
    "핵심 포인트 3 (예: 시장 심리 관련)"
  ],
  "risk_warnings": ["리스크 경고1", "리스크 경고2"] 최대 4개,
  "smart_money_flow": "기관/외국인 스마트 머니 흐름 분석 1~2문장",
  "catalyst_events": ["향후 예상 촉매 이벤트1", "이벤트2"] 최대 4개
}}

참고: {_DISCLAIMER_LINE}"""
