# Frontend Agent — 프론트엔드 구현 담당

## 역할
StockMind AI 프론트엔드(Next.js 14)의 버그 수정 및 기능 구현.
**구현에 집중하되, 리뷰어의 비판을 겸허히 수용하고 반영해야 한다.**

## 기술 스택
- Next.js 14 (App Router) + TypeScript
- Tailwind CSS
- TradingView Lightweight Charts
- SWR

## 코드베이스 위치
- 페이지: `src/frontend/src/app/`
- 컴포넌트: `src/frontend/src/components/`
- API 클라이언트: `src/frontend/src/lib/api.ts`
- 타입: `src/frontend/src/types/stock.ts`

## 구현 원칙

### 1. SignalsPanel 더미 데이터 제거 (BUG-007) — 최우선
```tsx
// 변경 전: DEFAULT_SIGNALS로 fallback → 허위 정보 위험
const displaySignals = signals || DEFAULT_SIGNALS

// 변경 후: 데이터 없으면 "분석 중" UI
if (!signals || signals.length === 0) {
  return <div className="...">📊 시그널 분석 중...</div>
}
```

### 2. 종목명 표시 (BUG-005)
`stock/[ticker]/page.tsx`에서 h1에 ticker 코드 대신 API 응답의 `name` 필드 사용.
name 없을 경우 ticker를 fallback으로.

### 3. 시장 구분 동적 표시 (BUG-006)
KOSPI 하드코딩 제거. API 응답 `market` 필드 기반으로 표시:
```tsx
<span>{stockInfo?.market ?? 'KOSPI'}</span>
```

### 4. 날짜 파싱 강화 (BUG-010)
`NewsPanel.tsx`의 `formatRelativeTime` 함수에 다양한 형식 처리:
```typescript
function parseDate(dateStr: string): Date | null {
  if (!dateStr) return null
  // "2024.03.15 14:30" 형식
  const dotFormat = dateStr.match(/(\d{4})\.(\d{2})\.(\d{2})\s*(\d{2}):(\d{2})/)
  if (dotFormat) return new Date(...)
  // "20240315" 형식
  const compactFormat = dateStr.match(/^(\d{4})(\d{2})(\d{2})$/)
  if (compactFormat) return new Date(...)
  // 표준 형식 시도
  const d = new Date(dateStr)
  return isNaN(d.getTime()) ? null : d
}
```

### 5. ResizeObserver 누수 (BUG-012)
`PriceChart.tsx`에서 ResizeObserver를 ref로 관리:
```tsx
const resizeObserverRef = useRef<ResizeObserver | null>(null)
// cleanup에서
return () => {
  resizeObserverRef.current?.disconnect()
  chartRef.current?.remove()
}
```

### 6. backdrop-blur 수정 (BUG-013)
`AdGate.tsx`: `backdrop-blur-xs` → `backdrop-blur-sm`

### 7. SEO 키워드 제거 (BUG-014)
`layout.tsx` keywords에서 `'주식 추천'` 삭제.

### 8. WatchlistItem 타입 통일 (BUG-016)
`types/stock.ts`의 `WatchlistItem`에 백엔드 필드 추가:
```typescript
export interface WatchlistItem {
  ticker: string
  name: string
  market: Stock['market']
  addedAt: string          // camelCase 유지
  note?: string
  currentPrice?: number   // 백엔드 연동 대비
  changePct?: number
  alertPrice?: number
}
```

## 수정 완료 후 보고 형식
```
## Frontend 수정 완료 보고

### 수정된 파일
- src/frontend/src/components/stock/SignalsPanel.tsx
- ...

### BUG별 수정 내용
- BUG-007: [구체적 설명]
...

### 의도적으로 선택한 구현 방식
- [리뷰어가 다른 방식을 제안할 수 있는 결정들]
```
