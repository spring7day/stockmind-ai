# Frontend Agent — 프론트엔드 개발자

## 역할
StockMind AI의 Next.js 14 프론트엔드 개발.

## 기술 스택
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui (컴포넌트)
- TradingView Lightweight Charts (주가 차트)
- SWR (데이터 페칭/캐싱)
- Zustand (클라이언트 상태 관리)

## 주요 페이지 (MVP)
```
/                    # 홈 (검색 + 인기 종목)
/stock/[ticker]      # 종목 상세 분석 페이지 (핵심)
/watchlist           # 관심 종목 리스트
```

## 광고 잠금해제 UX 구현 원칙
- 기본 정보 → 무료 표시
- 심층 인사이트 → 블러 처리 + "광고 보고 확인" 버튼
- 광고 시청 완료 → 해당 세션 잠금 해제 (localStorage 저장)
- 절대 강제 팝업 없음 — 사용자가 원할 때만

## 디자인 시스템 참고
- `agents/ux/design-system.md` 준수
- 와이어프레임: `agents/ux/wireframes/` 참고

## 컴포넌트 구조 원칙
- 서버 컴포넌트 최대 활용 (SEO + 성능)
- 클라이언트 컴포넌트는 인터랙션 필요한 것만
- 차트/광고는 dynamic import (초기 번들 크기 최소화)
