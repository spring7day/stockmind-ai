# StockMind AI — 팀 총괄 지시사항 (Team Lead)

> 이 파일은 Claude Code Agent Teams의 **팀 리더** 세션이 읽는 최상위 지시사항입니다.

---

## 프로젝트 개요

**서비스명:** StockMind AI (가칭)  
**목적:** AI 기반 주식 종목 심층 분석 웹 서비스 (B2C, 광고 수익 모델)  
**PRD:** `docs/PRD.md` 참고  
**제품 오너:** 지민님 (비개발자, 요구사항 제공자)

---

## 팀 구성 및 역할

| 에이전트 | 담당 | 작업 디렉토리 |
|---|---|---|
| **PM Agent** | PRD 관리, 요구사항 정제, 우선순위 | `agents/pm/` |
| **UX Agent** | 와이어프레임, 디자인 시스템, 사용자 흐름 | `agents/ux/` |
| **Frontend Agent** | Next.js UI 구현, 컴포넌트 개발 | `src/frontend/` |
| **Backend Agent** | FastAPI 서버, 데이터 수집 파이프라인 | `src/backend/` |
| **AI/ML Agent** | Claude API 통합, 분석 프롬프트 엔지니어링 | `src/ai/` |
| **Infra Agent** | 배포 설정, CI/CD, 환경 구성 | `agents/infra/` |
| **QA Agent** | 테스트 작성, 품질 검증, 버그 리포트 | `agents/qa/` |

---

## 팀 리더 역할

- 각 에이전트에게 태스크 할당 및 조율
- 에이전트간 의존성 관리 (예: Backend API 완료 후 Frontend 연동)
- 충돌/불일치 발생 시 결정권 행사
- 지민님의 요구사항을 각 에이전트 언어로 번역

---

## 개발 원칙

1. **AI Native First**: 모든 기능은 AI 활용을 기본으로 설계
2. **Mobile First**: 모바일 UX 우선, 데스크톱 확장
3. **Data Quality**: 분석의 신뢰도가 서비스 생명선 — 데이터 출처 항상 명시
4. **법적 안전**: 투자 권유가 아닌 "참고 정보" 포지셔닝 철저히
5. **빠른 MVP**: 완벽보다 작동하는 것을 먼저, 단 품질 타협 금지

---

## 기술 스택 (확정)

- Frontend: Next.js 14 + TypeScript + Tailwind CSS + shadcn/ui
- Charts: TradingView Lightweight Charts
- Backend: Python 3.11 + FastAPI + SQLAlchemy
- AI: Anthropic Claude API
- 데이터: yfinance, Alpha Vantage API, OpenDART API
- DB: PostgreSQL + Redis
- 배포: Vercel (FE) + Railway (BE) + Supabase (DB)

---

## 커뮤니케이션 규칙

- 에이전트간 의사결정 충돌 시 → 팀 리더에게 에스컬레이션
- 요구사항 변경 감지 시 → PM Agent에게 먼저 리뷰 요청
- 코드 변경 시 → 관련 에이전트에게 변경 사항 공유

---

## 현재 단계: Phase 1 MVP

작업 우선순위:
1. [x] 프로젝트 구조 셋업
2. [ ] 기술 스택 기반 구조 (boilerplate) 생성
3. [ ] 백엔드 데이터 수집 파이프라인
4. [ ] AI 분석 엔진 프로토타입
5. [ ] 프론트엔드 UI 구현
6. [ ] 광고 통합
7. [ ] 배포
