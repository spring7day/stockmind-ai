# StockMind AI — Bug Report

> QA 수행일: 2026-03-10
> 대상: `src/frontend/` + `src/backend/` 전체 정적 코드 분석
> QA Agent: Claude Sonnet 4.6

---

## 🔴 Critical (즉시 수정 필요)

### BUG-001: 프론트엔드 API 엔드포인트 불일치 — `/api/stocks/popular` 미구현

**위치:** `src/frontend/src/lib/api.ts:177`
**증상:** 프론트엔드가 `GET /api/stocks/popular`를 호출하지만 백엔드에 해당 엔드포인트가 존재하지 않음.

```typescript
// api.ts:177
return fetchApi<StockSummary[]>('/api/stocks/popular')
```

**백엔드 실제 라우터 (`stocks.py`)에서 `/popular` 라우트 없음:**
- `GET /search` — 종목 검색
- `GET /{ticker}` — 종목 상세
- `GET /{ticker}/analysis` — AI 분석
- `GET /{ticker}/news` — 뉴스
- `GET /{ticker}/signals` — 시그널

**영향:** MOCK_MODE=false일 때 홈 페이지 인기 종목 섹션이 404 에러 발생
**해결:** 백엔드에 `GET /api/stocks/popular` 엔드포인트 추가 또는 프론트 목 데이터 사용 유지

---

### BUG-002: 프론트엔드 API 엔드포인트 불일치 — `/api/stocks/{ticker}/price` 미구현

**위치:** `src/frontend/src/lib/api.ts:200`
**증상:** 프론트엔드가 `GET /api/stocks/{ticker}/price`를 호출하지만 백엔드에 해당 라우트가 없음.

```typescript
// api.ts:200
return fetchApi<StockPrice>(`/api/stocks/${ticker}/price`)
```

**백엔드에서 `/{ticker}` 라우트는 `StockInfo` 전체를 반환**하며, `StockPrice`만 반환하는 별도 `/price` 엔드포인트가 없음.

**추가 문제 — 응답 스키마 불일치:**
- 프론트 `StockPrice` 인터페이스: `currentPrice`, `openPrice`, `highPrice`, `lowPrice`, `closePrice`, `change`, `changePercent`
- 백엔드 `StockPrice` 모델: `current`, `open`, `high`, `low`, `prev_close`, `change`, `change_pct`

**필드명이 다름:** `currentPrice` vs `current`, `changePercent` vs `change_pct`, `openPrice` vs `open` 등

**영향:** MOCK_MODE=false일 때 모든 종목 상세 페이지가 404 또는 데이터 매핑 실패
**해결:** 백엔드에 `/price` 엔드포인트 추가하고 응답 필드명 통일

---

### BUG-003: 프론트엔드 분석 탭별 API 호출 불일치

**위치:** `src/frontend/src/lib/api.ts:225`

```typescript
return fetchApi<AnalysisResult>(`/api/stocks/${ticker}/analysis/${tab}`)
// 호출: /api/stocks/005930/analysis/technical
```

**백엔드 실제 라우트:**
```python
@router.get("/{ticker}/analysis", ...)  # 탭 파라미터 없음, 전체 분석 반환
```

백엔드는 탭별이 아닌 `AnalysisResult` 전체(technical + fundamental + hidden_insights + sentiment)를 한번에 반환함.

**추가 스키마 불일치:**
- 프론트 `AnalysisResult`: `tab`, `ticker`, `summary`, `score`, `signals`, `details`, `generatedAt`, `disclaimer`
- 백엔드 `AnalysisResult`: `ticker`, `name`, `technical`, `fundamental`, `hidden_insights`, `sentiment`, `overall_summary`, `disclaimer`, `analyzed_at`

구조가 완전히 다름. 프론트는 단일 플랫 구조, 백엔드는 중첩 객체 구조.

**영향:** MOCK_MODE=false 시 AI 분석 탭이 완전히 동작 불가
**해결:** 백엔드에 탭별 엔드포인트 추가하거나, 프론트엔드가 전체 분석 결과를 탭별로 파싱하도록 수정

---

### BUG-004: NewsItem 스키마 불일치

**위치:** `src/frontend/src/types/stock.ts:64-73`, `src/backend/app/models/stock.py:136-144`

**프론트 `NewsItem`:**
```typescript
id: string           // ← 백엔드에 없음
sentiment: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL'  // string vs enum
sentimentScore: number   // ← 백엔드에 없음
publishedAt: string      // camelCase
```

**백엔드 `NewsItem`:**
```python
title: str
source: str
url: Optional[str]
published_at: Optional[str]  # snake_case
summary: Optional[str]
sentiment: Optional[str]     # 타입 없음
is_disclosure: bool          # ← 프론트에 없음
```

**영향:** 뉴스 패널이 `id` 없이 key 오류, `sentimentScore` undefined로 `SentimentBadge` 렌더링 실패
**해결:** 스키마 통일 (id 생성 로직 추가, camelCase 통일, 필수 필드 동기화)

---

## 🟡 Warning (기능 영향 있음, 우선 수정 권장)

### BUG-005: 종목 상세 페이지에서 종목명 미표시

**위치:** `src/frontend/src/app/stock/[ticker]/page.tsx:83`

```tsx
{/* 종목명 (ticker로 임시 표시 — 실제는 API에서 name 받아야 함) */}
<h1 className="text-2xl font-bold text-text-primary">{ticker}</h1>
```

종목명이 아닌 ticker 코드(예: `005930`)가 h1에 표시됨. 코드 자체 주석에도 미완성임을 인정.

**영향:** UX 저하, SEO 불이익 (h1이 종목 코드)
**해결:** `getStockPrice` 응답 또는 별도 API에서 `name` 필드 사용

---

### BUG-006: 시장 구분 하드코딩 (KOSPI 고정)

**위치:** `src/frontend/src/app/stock/[ticker]/page.tsx:78`

```tsx
<span className="text-xs px-2 py-0.5 rounded-full bg-card border border-border text-text-muted">
  KOSPI
</span>
```

KOSDAQ 종목도 항상 "KOSPI"로 표시됨.

**영향:** 데이터 오표시 (KOSDAQ 종목 오인)
**해결:** API 응답에서 `market` 필드를 동적으로 표시

---

### BUG-007: SignalsPanel이 항상 더미 데이터 표시

**위치:** `src/frontend/src/components/stock/SignalsPanel.tsx:38-63, 66`

```typescript
const displaySignals = signals || DEFAULT_SIGNALS
```

`DEFAULT_SIGNALS`에 하드코딩된 "외국인 수급 5일 연속 순매수 전환", "내부자 매수 신고 3건 확인" 등의 문구가 실제 데이터처럼 모든 종목에 동일하게 표시될 위험 있음.

**영향:** 잘못된 정보 표시 위험 → 투자 오판 유도 가능성
**해결:** `signals`가 없을 때 더미 표시 대신 "분석 중" 또는 "데이터 없음" UI 표시

---

### BUG-008: `asyncio.get_event_loop()` Deprecation Warning

**위치:** `src/backend/app/services/data_collector.py:115, 161, 200, 232`

```python
loop = asyncio.get_event_loop()
result = await loop.run_in_executor(None, _fetch)
```

Python 3.10+에서 `asyncio.get_event_loop()`는 실행 루프 없는 환경에서 DeprecationWarning 발생. 권장 방식은 `asyncio.get_running_loop()`.

**영향:** Python 3.12+에서 오류 발생 가능
**해결:** `asyncio.get_event_loop()` → `asyncio.get_running_loop()` 또는 `asyncio.to_thread()` 사용

---

### BUG-009: Claude API 동기 호출 (블로킹 I/O)

**위치:** `src/backend/app/services/ai_analyzer.py:122-126, 175-180, 238-242, 289-294`

```python
async def analyze_technical(stock_info: StockInfo) -> TechnicalAnalysis:
    ...
    client = _get_client()
    message = client.messages.create(  # 동기 API 호출!
```

`anthropic.Anthropic` (동기 클라이언트) 사용 중. `asyncio.gather`로 병렬 실행하지만 내부적으로 blocking I/O가 이벤트 루프를 차단함.

**영향:** 고부하 시 다른 요청 처리가 블로킹되어 서버 응답 지연
**해결:** `anthropic.AsyncAnthropic` (비동기 클라이언트)로 교체

---

### BUG-010: 뉴스 날짜 파싱 오류 가능성

**위치:** `src/frontend/src/components/stock/NewsPanel.tsx:37-47`

```typescript
function formatRelativeTime(dateStr: string): string {
  const date = new Date(dateStr)
  const diffMins = Math.floor(diffMs / 60000)
```

백엔드 `published_at`이 `"2024.03.15 14:30"` (네이버 금융 형식) 또는 `"20240315"` (DART 형식)인 경우 `new Date(dateStr)` 파싱 실패 → `NaN` → 이상한 숫자 표시.

**영향:** 뉴스 목록에 `NaN분 전` 또는 `NaN일 전` 표시
**해결:** `published_at` 파싱 로직에 다양한 날짜 형식 지원 및 null 처리 추가

---

### BUG-011: 백엔드 응답이 `ApiResponse<T>` 래퍼 미사용

**위치:** `src/frontend/src/lib/api.ts:51-57`

```typescript
const json: ApiResponse<T> = await response.json()
if (!json.success) {
  throw new ApiError(500, json.error || '알 수 없는 오류가 발생했습니다')
}
return json.data
```

프론트는 `{success: bool, data: T}` 래퍼 형식을 기대하지만, 백엔드 FastAPI 라우터는 Pydantic 모델을 직접 반환 (래퍼 없음).

```python
# stocks.py
return StockInfo(**cached)  # 직접 반환, {success, data} 구조 아님
```

**영향:** MOCK_MODE=false 시 모든 API 호출이 `json.success` is undefined → `throw new ApiError(500, ...)` 발생
**해결:** 백엔드에 `ApiResponse` 미들웨어/공통 응답 래퍼 추가하거나, 프론트엔드가 직접 응답을 파싱하도록 수정

---

## 🟢 Minor (UI/기능 개선)

### BUG-012: PriceChart ResizeObserver cleanup 누락

**위치:** `src/frontend/src/components/stock/PriceChart.tsx:127-136`

```typescript
const resizeObserver = new ResizeObserver(...)
resizeObserver.observe(container)

return () => {
  resizeObserver.disconnect()  // 내부 return 안에 있음
}
// ...
return () => {        // 외부 cleanup (charts 제거)
  if (chartRef.current) { ... }
}
```

차트 useEffect에 `return` 이 두 개 있음. 내부 `import().then()` Promise 내부의 cleanup은 실제로 useEffect cleanup으로 등록되지 않음. 외부 cleanup만 실행되어 ResizeObserver가 누수될 수 있음.

**영향:** 컴포넌트 언마운트 시 ResizeObserver 메모리 누수
**해결:** ResizeObserver ref로 관리하고 외부 cleanup에서 disconnect 호출

---

### BUG-013: AdGate `backdrop-blur-xs` 비표준 Tailwind 클래스

**위치:** `src/frontend/src/components/ui/AdGate.tsx:186`

```tsx
<div className="absolute inset-0 flex flex-col items-center justify-center bg-background/80 backdrop-blur-xs">
```

`backdrop-blur-xs`는 Tailwind v3 기본 클래스가 아님 (`backdrop-blur-sm`이 최소값). 커스텀 설정 없으면 적용 안 됨.

**영향:** AdGate 오버레이 블러 효과 미적용
**해결:** `backdrop-blur-xs` → `backdrop-blur-sm` 변경 또는 tailwind.config.ts에 커스텀 값 추가

---

### BUG-014: 홈페이지 SEO 키워드에 "주식 추천" 포함

**위치:** `src/frontend/src/app/layout.tsx:15`

```typescript
keywords: ['주식', 'AI 분석', '주식 분석', '코스피', '코스닥', '주식 추천', '기술적 분석'],
```

"주식 추천"은 투자 권유성 키워드로, 자본시장법상 투자권유에 해당할 수 있음. 메타 키워드는 SEO 효과도 없으면서 법적 위험만 존재.

**영향:** 법적 리스크 (투자권유업 무허가 이슈)
**해결:** `'주식 추천'` → `'주식 심층분석'` 또는 삭제

---

### BUG-015: `_clean_expired()` 미호출 (메모리 누수)

**위치:** `src/backend/app/services/cache.py:137-143`

```python
def _clean_expired(self):
    """만료된 in-memory 캐시 항목을 정리합니다."""
```

이 메서드가 정의되어 있지만 어디서도 호출되지 않음. 장기 운영 시 in-memory 캐시가 무한 증가.

**영향:** Redis 없는 환경에서 장기 운영 시 메모리 증가
**해결:** `set()` 호출 시 주기적으로 또는 `get()` 시 expired 항목 제거 로직 추가

---

### BUG-016: `WatchlistItem` 타입 불일치 (프론트-백엔드)

**위치:** `src/frontend/src/types/stock.ts:91-97`

```typescript
export interface WatchlistItem {
  ticker: string
  name: string
  market: Stock['market']
  addedAt: string  // camelCase
  note?: string    // 백엔드에 없음
}
```

백엔드 `WatchlistItem` 모델:
```python
added_at: datetime   # snake_case
current_price: Optional[float]  # 프론트에 없음
change_pct: Optional[float]     # 프론트에 없음
alert_price: Optional[float]    # 프론트에 없음
```

프론트엔드 관심종목은 localStorage 전용이라 현재 문제없으나, 백엔드 연동 시 필드 불일치로 오류 발생.

**영향:** 향후 백엔드 연동 시 데이터 매핑 실패
**해결:** 공통 타입 정의 또는 응답 변환 레이어 추가

---

## 요약 통계

| 심각도 | 개수 |
|--------|------|
| 🔴 Critical | 4 |
| 🟡 Warning | 7 |
| 🟢 Minor | 5 |
| **합계** | **16** |

## 즉시 수정 필요 항목 (Critical)

백엔드-프론트엔드 실제 연동을 위해 아래 4가지 버그를 최우선으로 수정해야 합니다:

1. `GET /api/stocks/popular` 엔드포인트 추가
2. `GET /api/stocks/{ticker}/price` 엔드포인트 추가 (필드명 통일 포함)
3. `GET /api/stocks/{ticker}/analysis/{tab}` 탭별 엔드포인트 추가 또는 응답 구조 통일
4. 백엔드 `ApiResponse<T>` 래퍼 적용 또는 프론트엔드 직접 파싱으로 변경
