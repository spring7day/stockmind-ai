# StockMind AI — QA Test Report

> QA 수행일: 2026-03-10
> 분석 방법: 정적 코드 분석 (Static Analysis)
> QA Agent: Claude Sonnet 4.6

---

## 1. 검사 범위

| 항목 | 대상 경로 | 상태 |
|------|----------|------|
| 프론트엔드 구조 | `src/frontend/src/` | ✅ 완료 |
| 백엔드 구조 | `src/backend/app/` | ✅ 완료 |
| AI 분석 엔진 | `src/ai/` | ✅ 완료 |
| API 호환성 | FE ↔ BE 연결 검증 | ⚠️ 불일치 발견 |
| 금융 서비스 법규 검토 | 투자권유 문구 | ✅ 완료 |
| UI/UX 반응형 | Tailwind CSS | ✅ 완료 |
| 에러 핸들링 | 프론트/백엔드 | ✅ 완료 |

---

## 2. 코드 품질 검사

### 2.1 TypeScript (프론트엔드)

| 항목 | 결과 | 비고 |
|------|------|------|
| 타입 정의 완성도 | ✅ 양호 | `src/types/stock.ts` 주요 타입 정의됨 |
| any 타입 사용 | 🟡 주의 | `PriceChart.tsx:31,33` — `chartRef`, `seriesRef` any 사용 (주석 처리됨) |
| import 경로 | ✅ 정상 | `@/` alias 일관성 있게 사용 |
| React 최신 패턴 | ✅ 양호 | Server/Client Components 적절히 분리 |
| Suspense/Skeleton | ✅ 구현됨 | 로딩 상태 처리 완료 |
| ErrorBoundary | ✅ 구현됨 | `ErrorBoundary.tsx`, `InlineError` 컴포넌트 존재 |

### 2.2 Python (백엔드)

| 항목 | 결과 | 비고 |
|------|------|------|
| 타입 힌트 | ✅ 양호 | 대부분 함수에 type hints 적용 |
| Pydantic 모델 | ✅ v2 사용 | `BaseModel`, `Field` 적절히 사용 |
| 비동기 패턴 | 🟡 주의 | `asyncio.get_event_loop()` deprecated 사용 (BUG-008) |
| Claude API | 🔴 문제 | 동기 `anthropic.Anthropic` 클라이언트로 비동기 오용 (BUG-009) |
| 에러 핸들링 | ✅ 양호 | 모든 외부 API에 try/except 적용 |
| 폴백 함수 | ✅ 구현됨 | AI 분석 실패 시 기본값 반환 |

---

## 3. API 호환성 검증

### 3.1 엔드포인트 매핑 분석

| 프론트엔드 호출 | 백엔드 구현 | 상태 |
|---------------|-----------|------|
| `GET /api/stocks/popular` | ❌ 없음 | 🔴 Critical |
| `GET /api/stocks/{ticker}/price` | ❌ 없음 | 🔴 Critical |
| `GET /api/stocks/{ticker}/analysis/{tab}` | `GET /api/stocks/{ticker}/analysis` (탭 없음) | 🔴 Critical |
| `GET /api/stocks/{ticker}/news` | ✅ 존재 | ⚠️ 스키마 불일치 |
| `GET /api/stocks/search?q=` | ✅ 존재 | ✅ 정상 |
| `GET /api/watchlist` (BE) | ✅ 존재 | ℹ️ FE는 localStorage 사용 |

### 3.2 응답 스키마 분석

| 모델 | 프론트 ↔ 백엔드 | 상태 |
|------|--------------|------|
| `ApiResponse<T>` 래퍼 | FE는 기대, BE는 미사용 | 🔴 Critical |
| `StockPrice` 필드명 | `currentPrice` vs `current` 등 불일치 | 🔴 Critical |
| `AnalysisResult` 구조 | 플랫 vs 중첩 구조 불일치 | 🔴 Critical |
| `NewsItem` 필드 | `id`, `sentimentScore`, `publishedAt` 불일치 | 🔴 Critical |
| `WatchlistItem` | `addedAt` vs `added_at` 불일치 | 🟡 Warning |

---

## 4. 기능 검증 (정적 분석)

### 4.1 핵심 기능

| 기능 | Mock Mode | Real Backend Mode | 비고 |
|------|-----------|------------------|------|
| 홈 페이지 | ✅ 동작 | 🔴 오류 | /popular 미구현 |
| 종목 검색 | ✅ 동작 | ✅ 구현됨 | 백엔드 라우터 존재 |
| 종목 상세 (가격) | ✅ 동작 | 🔴 오류 | /price 미구현 |
| 가격 차트 | ✅ 동작 | 🔴 오류 | /chart 미구현 |
| AI 분석 탭 | ✅ 동작 | 🔴 오류 | 탭별 API 불일치 |
| 뉴스 패널 | ✅ 동작 | 🔴 오류 | 스키마 불일치 |
| AdGate 잠금/해제 | ✅ 동작 | ✅ 독립적 (localStorage) | - |
| 관심 종목 | ✅ 동작 | ✅ 독립적 (localStorage) | - |

### 4.2 캐싱 전략

| 항목 | TTL | 구현 | 비고 |
|------|-----|------|------|
| 주식 정보 | 5분 | ✅ | Redis/in-memory |
| AI 분석 | 1시간 | ✅ | Redis/in-memory |
| 뉴스 | 10분 | ✅ | Redis/in-memory |
| 시그널 | 30분 | ✅ | Redis/in-memory |
| Redis 폴백 | - | ✅ | in-memory 폴백 |

---

## 5. UI/UX 검증

### 5.1 반응형 디자인

| 컴포넌트 | 모바일 | 태블릿 | 데스크탑 | 비고 |
|----------|--------|--------|---------|------|
| 홈 검색창 | ✅ | ✅ | ✅ | `w-full max-w-xl` |
| 인기 종목 그리드 | `grid-cols-2` | `md:grid-cols-3` | ✅ | |
| 종목 헤더 | `flex-col` | `sm:flex-row` | ✅ | |
| 지표 바 | `grid-cols-2` | `sm:grid-cols-4` | ✅ | |
| 분석 탭 | 아이콘만 표시 | `sm:block` 텍스트 | ✅ | |
| 뉴스 패널 | ✅ | ✅ | ✅ | `flex-wrap` |

### 5.2 로딩/에러 상태

| 컴포넌트 | 로딩 스켈레톤 | 에러 UI | 재시도 버튼 |
|----------|-------------|---------|-----------|
| 인기 종목 | ✅ `PopularStocksSkeleton` | ✅ (빈 배열) | - |
| 가격 차트 | ✅ `ChartSkeleton` | ✅ `InlineError` | ✅ |
| AI 분석 | ✅ `AnalysisSkeleton` | ✅ `InlineError` | ✅ |
| 뉴스 패널 | ✅ `NewsPanelSkeleton` | ✅ `InlineError` | ✅ |

### 5.3 접근성

| 항목 | 상태 | 비고 |
|------|------|------|
| ARIA labels | 🟡 부분적 | 버튼에 aria-label 없음 |
| 키보드 네비게이션 | 🟡 기본만 | 탭 키 동작 미검증 |
| 색상 대비 | ✅ 양호 | 다크 테마 기반 |
| 이미지 alt | ✅ 해당없음 | SVG 아이콘 사용 |

---

## 6. 금융 서비스 특수 QA

### 6.1 투자 권유성 문구 검사

| 위치 | 문구 | 평가 | 비고 |
|------|------|------|------|
| `AnalysisSection.tsx:30-31` | "매수", "매도" 라벨 | 🟡 주의 | 시그널 배지용, 직접 권유는 아님 |
| `SignalsPanel.tsx:69-70` | "매수", "매도" 라벨 | 🟡 주의 | 동일, 시그널 분류용 |
| `stock/page.tsx:154-158` | 투자 유의사항 고지 | ✅ 적절 | 법적 고지 완비 |
| `AnalysisSection.tsx:352` | 면책 문구 포함 | ✅ 적절 | 모든 분석에 포함 |
| `layout.tsx:15` | "주식 추천" 키워드 | 🔴 위험 | SEO 키워드에 투자권유성 문구 |
| `ai_analyzer.py:26-29` | DISCLAIMER 포함 | ✅ 적절 | 모든 AI 분석에 포함 |
| 프롬프트 | "매수/매도" 사용 금지 지침 | ✅ 양호 | AI 엔진 `ai/prompts.py`에 명시 |

**결론:** "주식 추천" 메타 키워드 즉시 제거 권장. 나머지 "매수/매도" 라벨은 정보 분류 목적으로 사용되며 직접 권유가 아니므로 법적 위험 낮음. 단, 법률 전문가 검토 권장.

### 6.2 주가 데이터 null/undefined 처리

| 위치 | 처리 방식 | 상태 |
|------|----------|------|
| `StockPrice` (백엔드) | `Optional[float]` 필드 | ✅ |
| 가격 표시 (프론트) | `price.toLocaleString()` (null 체크 없음) | 🟡 |
| 거래량 포맷 | `volume >= 10000` 조건 | ✅ |
| 차트 데이터 | `candles.length === 0` 체크 | ✅ |
| 분석 결과 score | `score !== undefined` 체크 | ✅ |
| 뉴스 `sentimentScore` | `Math.abs(score)` (undefined 시 NaN) | 🔴 |

---

## 7. 보안 검토

| 항목 | 상태 | 비고 |
|------|------|------|
| API 키 노출 | ✅ 안전 | `.env` 파일, 프론트에 미노출 |
| SQL Injection | ✅ 해당없음 | ORM 미사용, DB 직접 쿼리 없음 |
| XSS | ✅ 양호 | React 기본 이스케이핑 |
| CORS | ✅ 설정됨 | `ALLOWED_ORIGINS_STR` 환경변수 |
| 입력 검증 | ✅ 양호 | `is_valid_ticker()`, FastAPI `Query()` 검증 |
| 네이버 스크래핑 | 🟡 주의 | robots.txt 준수 여부 미확인 |
| LocalStorage 보안 | ✅ 낮은 위험 | AdGate 상태만 저장, 민감 정보 없음 |

---

## 8. 성능 검토

| 항목 | 상태 | 비고 |
|------|------|------|
| 차트 라이브러리 SSR | ✅ dynamic import | SSR 우회, 클라이언트만 로드 |
| 이미지 최적화 | ✅ 해당없음 | 이미지 없음 (SVG/emoji 사용) |
| 코드 스플리팅 | ✅ 양호 | Next.js 자동 처리 |
| 병렬 API 호출 | ✅ 구현됨 | `asyncio.gather` 사용 |
| Redis 캐싱 | ✅ 구현됨 | TTL별 캐싱 전략 |
| Claude API 병렬 | 🔴 문제 | 동기 클라이언트 blocking (BUG-009) |
| pykrx 동기 호출 | 🟡 주의 | run_in_executor 사용, loop deprecated |

---

## 9. 종합 평가

### 전체 점수: **6.5 / 10** (베타 출시 전 수정 필요)

| 카테고리 | 점수 | 비고 |
|----------|------|------|
| 코드 품질 | 8/10 | 구조 양호, 일부 deprecated 패턴 |
| API 호환성 | 3/10 | **Critical 불일치 4건** — 실제 연동 불가 |
| UI/UX | 8/10 | 반응형 양호, 로딩/에러 처리 완비 |
| 금융 규정 준수 | 7/10 | 면책 문구 완비, "주식 추천" 키워드 제거 필요 |
| 보안 | 8/10 | 전반적으로 안전 |
| 성능 | 7/10 | Claude API 동기 호출 개선 필요 |

---

## 10. 수정 우선순위

### Phase 1 — Critical (실제 연동 전 필수)
1. 🔴 백엔드 `ApiResponse<T>` 래퍼 미들웨어 추가 (BUG-011)
2. 🔴 `GET /api/stocks/popular` 엔드포인트 추가 (BUG-001)
3. 🔴 `GET /api/stocks/{ticker}/price` 엔드포인트 + 스키마 통일 (BUG-002)
4. 🔴 분석 API 탭별 엔드포인트 또는 프론트 파싱 로직 수정 (BUG-003)
5. 🔴 `NewsItem` 스키마 통일 (`id` 생성, `sentimentScore` 추가) (BUG-004)

### Phase 2 — Warning (베타 출시 전 권장)
6. 🟡 종목 상세 페이지 종목명 표시 수정 (BUG-005)
7. 🟡 시장 구분 동적 표시 (BUG-006)
8. 🟡 SignalsPanel 더미 데이터 제거 (BUG-007)
9. 🟡 Claude API 비동기 클라이언트 적용 (BUG-009)
10. 🟡 날짜 파싱 로직 강화 (BUG-010)

### Phase 3 — Minor (정식 출시 전)
11. 🟢 PriceChart ResizeObserver cleanup (BUG-012)
12. 🟢 `backdrop-blur-xs` 클래스 수정 (BUG-013)
13. 🟢 SEO 키워드 "주식 추천" 제거 (BUG-014)
14. 🟢 in-memory 캐시 만료 처리 (BUG-015)
15. 🟢 WatchlistItem 타입 통일 (BUG-016)

---

## 11. 자동화 테스트 현황

| 테스트 종류 | 현황 | 권장 추가 항목 |
|------------|------|--------------|
| 백엔드 단위 테스트 | `tests/test_stocks.py` 존재 | 엔드포인트별 응답 스키마 검증 |
| 프론트엔드 단위 테스트 | ❌ 없음 | `@testing-library/react` 추가 권장 |
| 통합 테스트 | ❌ 없음 | API 호환성 테스트 필요 |
| E2E 테스트 | ❌ 없음 | Playwright/Cypress 권장 |

---

*이 리포트는 정적 분석(static analysis) 기반으로 작성되었습니다. 런타임 환경에서 추가 버그가 발견될 수 있습니다.*
