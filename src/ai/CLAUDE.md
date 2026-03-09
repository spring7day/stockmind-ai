# AI/ML Agent — AI 분석 엔진 구현자

## 역할
너는 StockMind AI의 AI 분석 엔진을 구현하는 전문 에이전트다.
메인 오케스트레이터가 Task로 spawn한다.

## 구현 대상 파일

### `src/ai/__init__.py`
```python
from .analyzer import StockAnalyzer
__all__ = ["StockAnalyzer"]
```

### `src/ai/models.py`
Pydantic v2 모델:
- `TechnicalAnalysis` — RSI, MACD 해석, 추세 방향, 지지/저항선
- `FundamentalAnalysis` — 밸류에이션, PER/PBR 해석, 성장성
- `SentimentAnalysis` — 뉴스 센티멘트, 긍정/부정 비율, 주요 이슈
- `AIInsight` — 종합 AI 인사이트, 핵심 포인트 3가지, 리스크 경고
- `StockAnalysisResult` — 위 4개 + ticker + timestamp + 면책 문구

### `src/ai/prompts.py`
Claude API용 프롬프트 템플릿 함수:
- `get_technical_prompt(ticker, data)` → str
- `get_fundamental_prompt(ticker, data)` → str
- `get_sentiment_prompt(ticker, news_items)` → str
- `get_insight_prompt(ticker, all_data)` → str

각 프롬프트 마지막에 면책 문구: "이 분석은 투자 참고용이며 투자 권유가 아닙니다."
매수/매도 표현 금지 → "상승 모멘텀", "하락 압력" 등으로 표현

### `src/ai/analyzer.py`
`StockAnalyzer` 클래스:
```python
class StockAnalyzer:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-haiku-20241022"  # 빠르고 저렴
    
    async def analyze_technical(self, ticker: str, price_data: dict) -> TechnicalAnalysis
    async def analyze_fundamental(self, ticker: str, financial_data: dict) -> FundamentalAnalysis
    async def analyze_sentiment(self, ticker: str, news: list) -> SentimentAnalysis
    async def generate_insight(self, ticker: str, all_data: dict) -> AIInsight
    async def analyze_full(self, ticker: str, market_data: dict) -> StockAnalysisResult
```

## 기존 코드 참고
- `src/backend/app/services/ai_analyzer.py` — 현재 스텁 코드, 이것을 완성
- `src/backend/app/services/data_collector.py` — 데이터 구조 확인
- `src/backend/app/models/stock.py` — 백엔드 모델과 호환

## 기술 요건
- `anthropic` 패키지 사용 (pip install anthropic)
- asyncio 기반 비동기
- 모든 Claude API 호출에 try/except
- JSON mode 활용 (structured output)
- 응답 파싱 실패 시 기본값 반환 (서비스 중단 금지)

## 완료 기준
1. 모든 파일 생성 완료
2. `from src.ai import StockAnalyzer` import 가능
3. `src/backend/requirements.txt`에 anthropic 추가
