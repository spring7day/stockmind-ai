# StockMind AI — 버그 수정 검증 리포트

> 검증일: 2026-03-10
> 검증 방법: 정적 코드 분석
> 검증 대상: Backend (stocks.py, response.py, stock.py, __init__.py, ai_analyzer.py, cache.py, data_collector.py) + Frontend (SignalsPanel.tsx, page.tsx, NewsPanel.tsx, PriceChart.tsx, AdGate.tsx, layout.tsx, stock.ts, api.ts)

---

## 검증 결과 요약

| 버그 ID | 심각도 | 수정 여부 | 검증 결과 |
|---------|--------|----------|----------|
| BUG-001 | Critical | PASS | `/popular` 엔드포인트 추가, ApiResponse 래퍼 적용, 프론트가 `response.data` 파싱 |
| BUG-002 | Critical | PASS | `/{ticker}/price` 엔드포인트 추가, StockPriceResponse(camelCase)로 필드명 통일 |
| BUG-003 | Critical | PASS | `/{ticker}/analysis/{tab}` 엔드포인트 추가, AnalysisResult 전체를 탭별로 변환 |
| BUG-004 | Warning  | PASS | NewsItem에 id(UUID), publishedAt, sentimentScore, isDisclosure 추가 + 양방향 동기화 |
| BUG-005 | Warning  | PASS | stockInfo.name 사용, getStockInfo() 별도 호출, mock fallback name=ticker 처리 |
| BUG-006 | Warning  | PASS | stockInfo.market 동적 표시 |
| BUG-007 | Warning  | PASS | DEFAULT_SIGNALS 완전 제거, signals 없을 때 "시그널 데이터를 분석 중입니다" UI |
| BUG-008 | Warning  | PASS (미수정 대상, 이미 수정됨) | data_collector.py에서 asyncio.get_running_loop() 사용 확인 |
| BUG-009 | Warning  | PASS | anthropic.AsyncAnthropic 사용, await client.messages.create() 적용 |
| BUG-010 | Warning  | PASS | parseDate() 함수 추가 — ISO 8601, 네이버금융, DART 형식 처리, null 처리 |
| BUG-011 | Critical | PASS | ApiResponse 모델 신규 생성, ok()/fail() 클래스 메서드, 프론트 fetchApi가 response.data 파싱 |
| BUG-012 | Minor    | PASS | resizeObserverRef 도입, 외부 cleanup에서 disconnect() + null 초기화 |
| BUG-013 | Minor    | PASS | backdrop-blur-sm 사용 확인 |
| BUG-014 | Minor    | PASS | '주식 추천' 제거, '주식 심층분석'으로 대체 |
| BUG-015 | Minor    | PASS | set() 호출 시 100회마다 _clean_expired() 자동 호출 |
| BUG-016 | Minor    | PASS | WatchlistItem에 currentPrice?, changePct?, alertPrice? 추가 |

---

## 상세 검증 내용

### Phase 1 — Critical 버그 (4건)

#### BUG-001: `/popular` 엔드포인트

- **파일**: `src/backend/app/routers/stocks.py` L191-231
- **검증**: `@router.get("/popular")` 라우트 존재. 반환 타입 `ApiResponse[List[StockSummaryResponse]]`. `ApiResponse.ok(items)` 반환.
- **프론트 파싱**: `api.ts` L435 — `fetchApi<ApiResponse<BackendStockSummaryItem[]>>('/api/stocks/popular')`, `response.data` 파싱.
- **판정**: PASS. 단, 주의사항 있음 → 아래 잔존 이슈 참조.

#### BUG-002: `/{ticker}/price` 엔드포인트 + 스키마

- **파일**: `src/backend/app/routers/stocks.py` L266-303, `src/backend/app/models/stock.py` L55-93
- **검증**: `@router.get("/{ticker}/price")` 존재. `StockPriceResponse` 모델에 `currentPrice`, `openPrice`, `highPrice`, `lowPrice`, `closePrice`, `change`, `changePercent`, `volume`, `marketCap?`, `updatedAt` 포함.
- **프론트 파싱**: `api.ts` L491 — `fetchApi<ApiResponse<StockPrice>>('/api/stocks/${ticker}/price')`, `response.data` 직접 반환. `StockPrice` 인터페이스(types/stock.ts L13-25)와 필드명 완전 일치.
- **판정**: PASS.

#### BUG-003: 탭별 분석

- **파일**: `src/backend/app/routers/stocks.py` L439-505
- **검증**: `@router.get("/{ticker}/analysis/{tab}")` 존재. 유효 탭: `technical|fundamental|insights|sentiment`. `_map_analysis_to_tab()` 헬퍼가 `AnalysisResult` → `TabAnalysisResult` 변환. `TabAnalysisResult` 구조: `{tab, ticker, summary, score?, details, generatedAt, disclaimer}` — 프론트 `AnalysisResult` 인터페이스와 일치.
- **프론트 파싱**: `api.ts` L521 — 백엔드 `/analysis` 전체를 받아 `mapBackendAnalysisToTab()`으로 탭별 변환. 프론트가 `/analysis/{tab}` 엔드포인트를 직접 호출하지 않고 `/analysis` 전체를 사용하는 방식으로 구현됨. 양쪽 모두 동작하는 이중 경로.
- **판정**: PASS. 프론트는 탭별 엔드포인트 대신 전체 분석을 받아 클라이언트 파싱하는 방식을 채택 — 이는 허용되는 구현이며, 백엔드 탭별 엔드포인트는 미래 최적화용으로 준비됨.

#### BUG-011: ApiResponse 래퍼

- **파일**: `src/backend/app/models/response.py` (신규)
- **검증**: `ApiResponse(BaseModel, Generic[T])` — `success: bool`, `data: Optional[T]`, `error: Optional[str]`. `ok(data)` / `fail(error)` 클래스 메서드 구현.
- **적용 범위**: `/popular`, `/search`, `/{ticker}/price`, `/{ticker}/analysis/{tab}`, `/{ticker}/news`, `/{ticker}/signals` — ApiResponse 래퍼 적용. 기존 `/{ticker}`, `/{ticker}/analysis` — 직접 반환 유지(기존 호환성).
- **프론트 파싱**: `api.ts` L37-57 — `fetchApi`가 래퍼 없이 직접 파싱. 신규 엔드포인트 호출 시 `fetchApi<ApiResponse<T>>` 후 `response.data` 추출. 에러 시 `ApiError` throw.
- **판정**: PASS. 단, `/{ticker}` (StockInfo 직접 반환)와 `/{ticker}/analysis` (AnalysisResult 직접 반환)는 래퍼 미적용 — 기존 호환성 유지 의도이며, 실제 프론트 코드도 이 엔드포인트를 `fetchApi<BackendStockInfo>`, `fetchApi<BackendAnalysisResult>`로 래퍼 없이 호출하므로 일관성 유지됨.

---

### Phase 2 — Warning 버그 (7건)

#### BUG-004: NewsItem 스키마

- **파일**: `src/backend/app/models/stock.py` L215-238
- **검증**: `id: str = Field(default_factory=lambda: str(uuid.uuid4()))` — UUID 자동 생성. `publishedAt: Optional[str]` 추가. `sentimentScore: Optional[float]` 추가. `isDisclosure: bool` 추가. `model_post_init`에서 `published_at ↔ publishedAt`, `is_disclosure → isDisclosure` 동기화.
- **프론트 활용**: `api.ts` L316-338 `mapBackendNewsItem()` — `item.id || String(index + 1)`, `item.publishedAt || item.published_at`, `item.sentimentScore ?? 0`, isDisclosure 미사용(프론트 NewsItem 타입에 없음).
- **판정**: PASS. isDisclosure는 백엔드에만 추가되고 프론트 NewsItem 타입에는 없으나, 프론트는 해당 필드를 사용하지 않으므로 기능 영향 없음.

#### BUG-005: 종목명 표시

- **파일**: `src/frontend/src/app/stock/[ticker]/page.tsx` L62-84
- **검증**: `getStockInfo(ticker)` 별도 호출 추가 (L62). `{stockInfo.name}`으로 h1 표시 (L84). Mock 폴백: `name: ticker` — ticker로 표시되지만 빈 string 없음. 실제 API 연결 시 name 필드 사용.
- **판정**: PASS.

#### BUG-006: market 동적 표시

- **파일**: `src/frontend/src/app/stock/[ticker]/page.tsx` L78-79
- **검증**: `{stockInfo.market}` 동적 표시. KOSPI/KOSDAQ 하드코딩 제거.
- **판정**: PASS.

#### BUG-007: SignalsPanel 더미 데이터 (금융 규정)

- **파일**: `src/frontend/src/components/stock/SignalsPanel.tsx` L38
- **검증**: `const displaySignals = signals && signals.length > 0 ? signals : []`. `DEFAULT_SIGNALS` 상수 완전 제거 확인. `displaySignals.length === 0`일 때 L111-114에서 "시그널 데이터를 분석 중입니다." 안내 UI 표시.
- **판정**: PASS. 허위 투자 정보 표시 불가 구조 확인.

#### BUG-008: `asyncio.get_running_loop()` (수정 대상 아님, 확인용)

- **파일**: `src/backend/app/services/data_collector.py`
- **검증**: L75 `asyncio.get_running_loop()`, L153 `asyncio.get_running_loop()`, L191 `asyncio.get_running_loop()`, L221 `asyncio.get_running_loop()`, L255 `asyncio.get_running_loop()`. `stocks.py` L355에서도 `asyncio.get_running_loop()` 사용.
- **판정**: PASS. 이미 `get_running_loop()` 사용 중.

#### BUG-009: AsyncAnthropic

- **파일**: `src/backend/app/services/ai_analyzer.py`
- **검증**: L36 `def _get_client() -> anthropic.AsyncAnthropic`. L40 `return anthropic.AsyncAnthropic(api_key=...)`. L122 `message = await client.messages.create(...)`. L175, L233, L289도 동일. 모든 analyze_* 함수가 `async def`.
- **판정**: PASS.

#### BUG-010: 날짜 파싱

- **파일**: `src/frontend/src/components/stock/NewsPanel.tsx` L36-60
- **검증**: `parseDate()` 함수 구현. ISO 8601 → `new Date(dateStr)` 우선 시도. 네이버금융 형식 `"2024.03.15 14:30"` 및 `"2024.03.15 14:30:45"` → 정규식 `/^(\d{4})\.(\d{2})\.(\d{2})\s+(\d{2}):(\d{2})(?::\d{2})?$/` 처리. DART 형식 `"20240315"` → 정규식 `/^(\d{4})(\d{2})(\d{2})$/` 처리. 파싱 실패 시 `null` 반환. `formatRelativeTime()`에서 null 처리 → `dateStr || '날짜 없음'` 반환.
- **판정**: PASS. 3가지 형식 모두 처리 확인.

---

### Phase 3 — Minor 버그 (5건)

#### BUG-012: ResizeObserver cleanup

- **파일**: `src/frontend/src/components/stock/PriceChart.tsx` L34, L128-148
- **검증**: `resizeObserverRef = useRef<ResizeObserver | null>(null)` 선언. import().then() 내부에서 `resizeObserverRef.current = new ResizeObserver(...)`, `resizeObserverRef.current.observe(container)`. 외부 useEffect cleanup (L139-148)에서 `resizeObserverRef.current?.disconnect()`, `resizeObserverRef.current = null`, `chartRef.current?.remove()`.
- **판정**: PASS. ref로 외부 cleanup에서 disconnect 확인.

#### BUG-013: AdGate backdrop-blur

- **파일**: `src/frontend/src/components/ui/AdGate.tsx` L186
- **검증**: `backdrop-blur-sm` 사용 확인. `backdrop-blur-xs` 제거 확인.
- **판정**: PASS.

#### BUG-014: SEO 키워드 '주식 추천'

- **파일**: `src/frontend/src/app/layout.tsx` L15
- **검증**: keywords 배열: `['주식', 'AI 분석', '주식 분석', '코스피', '코스닥', '주식 심층분석', '기술적 분석']`. '주식 추천' 없음. '주식 심층분석'으로 대체.
- **판정**: PASS.

#### BUG-015: `_clean_expired()` 호출

- **파일**: `src/backend/app/services/cache.py` L111-115
- **검증**: `set()` 메서드 내 `self._set_count += 1`, `if self._set_count >= 100: self._clean_expired(); self._set_count = 0`. `_clean_expired()` L143-148 구현 확인.
- **판정**: PASS. 100회 set 호출마다 자동 정리.

#### BUG-016: WatchlistItem 타입

- **파일**: `src/frontend/src/types/stock.ts` L91-101
- **검증**: `currentPrice?: number`, `changePct?: number`, `alertPrice?: number` 추가 확인. `addedAt: string` 유지 (localStorage 전용).
- **판정**: PASS.

---

## 신규 버그 도입 여부 검토

### Mock 모드 동작

- `api.ts` L18: `const MOCK_MODE = process.env.NEXT_PUBLIC_ENABLE_MOCK_DATA === 'true' || !process.env.NEXT_PUBLIC_API_URL`
- 각 API 함수 첫 줄에 `if (MOCK_MODE) return MOCK_...` 처리 유지.
- **판정**: PASS. Mock 모드 정상 동작.

### Import 오류 가능성

- `models/__init__.py`: `StockPriceResponse`, `StockSummaryResponse`, `TabAnalysisResult` 신규 추가 — `__all__` 포함 확인.
- `stocks.py`: `from app.models.response import ApiResponse`, `from app.models.stock import (..., StockPriceResponse, StockSummaryResponse, TabAnalysisResult)` — 모두 실제 정의된 클래스.
- **판정**: PASS. Import 오류 없음.

### TypeScript undefined 처리

- `page.tsx`: `priceData`, `stockInfo` — try/catch로 감싸고 실패 시 `notFound()` 호출. undefined 접근 위험 없음.
- `SignalsPanel.tsx`: `signals && signals.length > 0` — undefined 안전 처리.
- `NewsPanel.tsx`: `parseDate()` null 반환 처리, `formatRelativeTime()` null 가드.
- `api.ts`: `mapBackendNewsItem()` — `item.sentimentScore ?? 0`, `item.id || String(index + 1)` null coalescing 처리.
- **판정**: PASS.

### 잠재적 주의사항 (신규 발견)

#### 주의-A: `/{ticker}/analysis`와 `/{ticker}/analysis/{tab}` 라우트 충돌 가능성

- FastAPI는 경로 파라미터와 정적 경로가 충돌하면 등록 순서에 따라 우선순위 결정.
- `stocks.py`에서 `/{ticker}/analysis` (L392)가 `/{ticker}/analysis/{tab}` (L439)보다 먼저 등록됨.
- `GET /api/stocks/005930/analysis/technical` 요청 시, FastAPI가 `/{ticker}/analysis`로 matching하고 `technical`을 다음 경로 세그먼트로 인식할 수 있음 → **404가 아닌 `/{ticker}`에 `analysis` 값이 들어가거나**, 실제로는 FastAPI가 고정 세그먼트 `/analysis/{tab}`을 `/{ticker}/analysis`보다 우선시하므로 정상 동작 가능.
- FastAPI는 구체적인 경로 패턴을 더 높게 우선시하므로 실제로는 문제 없을 가능성이 높으나, 런타임 테스트 필요.
- **심각도**: 낮음 (정적 분석으로 확인 불가, 런타임 검증 권장).

#### 주의-B: `src/ai/analyzer.py`의 동기 클라이언트는 미수정

- `src/ai/analyzer.py` L82: `self.client = anthropic.Anthropic(api_key=api_key)` — 동기 클라이언트 사용.
- 이 파일은 수정 대상 목록에 없었으며, 실제 백엔드 서비스(`src/backend/app/services/ai_analyzer.py`)는 BUG-009 수정으로 AsyncAnthropic 사용. `src/ai/analyzer.py`는 별도 엔진으로, `src/backend`에서는 직접 사용하지 않음.
- **심각도**: 없음 (현재 백엔드 경로 아님).

#### 주의-C: `NewsItem.model_post_init` — Pydantic v2 호환성

- `stock.py` L229: `def model_post_init(self, __context) -> None:` — Pydantic v2 전용.
- `object.__setattr__`를 사용하는 이유는 Pydantic v2 frozen 모델이 아닌 경우에도 직접 속성 설정을 위함. frozen 모델이 아니므로 일반 `self.publishedAt = ...` 사용 가능했으나, 기능상 문제 없음.
- **심각도**: 없음.

---

## 잔존 이슈

**수정되지 않은 버그:** 없음. 16건 모두 수정됨.

**신규 발견 잠재 이슈:**

1. **주의-A** (낮음): `/{ticker}/analysis`와 `/{ticker}/analysis/{tab}` FastAPI 라우트 우선순위 — 런타임 테스트 권장.
2. **주의-B** (없음): `src/ai/analyzer.py` 동기 클라이언트 — 현재 백엔드 경로에서 미사용.
3. **주의-C** (없음): `model_post_init` object.__setattr__ — 기능 문제 없음.

---

## 최종 판정

**PASS**

- 모든 Critical 버그 4건 수정 완료 (BUG-001, 002, 003, 011)
- 모든 Warning 버그 7건 수정 완료 (BUG-004, 005, 006, 007, 008, 009, 010)
- 모든 Minor 버그 5건 수정 완료 (BUG-012, 013, 014, 015, 016)
- Mock 모드 정상 동작 확인
- Import 오류 없음
- TypeScript undefined 처리 적절
- 신규 Critical/Warning 버그 도입 없음
- 금융 규정 관련 허위 데이터 표시 위험 제거 (BUG-007) 확인

**런타임 검증 권장 사항:**
- FastAPI 라우트 `/{ticker}/analysis/{tab}` 실제 호출 테스트
- 네이버금융/DART 날짜 형식 parseDate 실제 데이터 파싱 테스트
- AsyncAnthropic API 호출 비동기 동작 테스트
