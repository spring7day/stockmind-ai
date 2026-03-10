# StockMind AI — 프로젝트 컨텍스트

> 이 파일은 모든 팀원(teammate)이 공통으로 읽는 프로젝트 컨텍스트다.
> Agent Teams 방식으로 운영되며, 팀원들은 공유 작업 목록을 통해 자율 조율한다.

---

## 프로젝트 개요

- **서비스명:** StockMind AI
- **목적:** AI 기반 주식 종목 심층 분석 웹 서비스 (B2C, 광고 수익 모델)
- **워크디렉토리:** `/Users/jimin/.openclaw/workspace/projects/stockmind`

---

## 기술 스택

- **백엔드:** FastAPI (`src/backend/`)
- **프론트엔드:** Next.js 14 (`src/frontend/`)
- **AI 엔진:** `src/ai/`

---

## 팀 역할 정의

팀원 생성 시 아래 역할을 기준으로 프롬프트를 작성한다.

| 역할 | 담당 |
|------|------|
| **Backend** | FastAPI 백엔드 구현/수정. `src/backend/` 소유 |
| **Frontend** | Next.js 프론트엔드 구현/수정. `src/frontend/` 소유 |
| **Reviewer** | 구현 코드 비판적 리뷰. 반드시 문제점을 지적해야 하며, 칭찬만 하는 리뷰는 무효 |
| **QA** | 정적 분석 및 기능 검증. 버그/부작용 확인 후 SHIP/HOLD 판정 |
| **PM** | 우선순위 결정, 충돌 중재, MVP 범위 판단 |

---

## 개발 원칙

### 디베이트 기반 개발
모든 구현은 아래 사이클로 진행한다:

```
구현 → 리뷰(비판) → 수정 반영 → QA 검증
```

- 팀원들은 공유 작업 목록에서 작업을 자율 요청한다
- 파일 충돌 방지: Backend는 `src/backend/`, Frontend는 `src/frontend/`만 편집
- 의견 충돌 시 PM이 최종 판단

### 파일 소유권
- `src/backend/` → Backend 팀원 전용
- `src/frontend/` → Frontend 팀원 전용
- `src/ai/` → 공통 (수정 전 다른 팀원에게 알릴 것)

---

## 현재 상태

- 기본 구조 구현 완료 (백엔드/프론트엔드/AI 엔진)
- 진행 중인 이슈는 `agents/qa/bug-report.md` 참고

---

## 완료 보고

작업 완료 후 리더에게 아래 정보를 포함해 보고:
1. 수정/구현한 파일 목록
2. 변경 내용 요약
3. 남은 이슈 (있다면)
