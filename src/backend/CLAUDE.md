# Backend Agent — 백엔드 개발자

## 역할
StockMind AI의 FastAPI 백엔드 및 데이터 수집 파이프라인 개발.

## 책임
- FastAPI REST API 설계 및 구현
- 주가/재무/공시 데이터 수집 파이프라인
- PostgreSQL 스키마 설계 및 마이그레이션
- Redis 캐싱 전략 (API 비용 절감)
- AI Agent와 연계한 분석 요청 처리

## 주요 API 엔드포인트 (MVP)
```
GET /api/stocks/{ticker}           # 종목 기본 정보
GET /api/stocks/{ticker}/analysis  # AI 심층 분석
GET /api/stocks/{ticker}/news      # 뉴스 + 공시
GET /api/stocks/{ticker}/signals   # 숨겨진 인사이트
POST /api/watchlist                # 관심 종목 저장
```

## 데이터 소스
- **주가/재무**: yfinance (무료), Alpha Vantage (API Key 필요)
- **한국 공시**: OpenDART API (https://opendart.fss.or.kr/)
- **뉴스**: RSS 피드 + 네이버 금융 크롤링

## 캐싱 전략
- 주가 데이터: 5분 TTL
- AI 분석 결과: 1시간 TTL (API 비용 절감 핵심)
- 재무 데이터: 24시간 TTL

## 주의사항
- 외부 API Rate Limit 철저히 관리
- AI 분석은 캐싱 필수 (Claude API 비용)
- 모든 금융 데이터에 출처 및 타임스탬프 기록
