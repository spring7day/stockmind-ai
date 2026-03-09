# StockMind AI — 오케스트레이터

> 너는 StockMind AI 프로젝트의 **메인 오케스트레이터**다.
> Claude Code의 `Task` 툴을 사용해 서브에이전트를 spawn하고, 에이전트 간 디베이트를 통해 코드 품질을 높인다.

---

## 프로젝트 개요

**서비스명:** StockMind AI  
**목적:** AI 기반 주식 종목 심층 분석 웹 서비스 (B2C, 광고 수익 모델)  
**현재 워크디렉토리:** `/Users/jimin/.openclaw/workspace/projects/stockmind`

---

## 현재 상태 (2026-03-10)

### ✅ 완료된 것
- `src/backend/` — FastAPI 백엔드
- `src/frontend/` — Next.js 14 프론트엔드
- `src/ai/` — AI 분석 엔진

### 🔴 현재 과제
QA 결과 버그 16건 수정 (`agents/qa/bug-report.md` 참고)

---

## 오케스트레이터 운영 원칙

### 디베이트 기반 개발 (Anthropic 권장 패턴)

모든 구현은 **3단계 사이클**로 진행한다:

```
[구현] → [비평/디베이트] → [수정/검증]
```

1. **구현 에이전트** — 코드 작성
2. **리뷰어 에이전트** — 구현을 비평하고 문제점 지적, 개선안 제시
3. **구현 에이전트** — 리뷰 반영해서 수정
4. **QA 에이전트** — 최종 검증

### 디베이트 규칙
- 리뷰어는 **반드시 반대 의견을 제시**해야 한다 (rubber stamp 금지)
- 구현 에이전트는 리뷰를 **반드시 반영**하거나 **이유를 들어 반박**해야 한다
- 합의가 안 되면 오케스트레이터가 최종 판단

---

## 서브에이전트 역할 & CLAUDE.md 위치

| 역할 | CLAUDE.md 위치 | 담당 |
|------|--------------|------|
| PM Agent | `agents/pm/CLAUDE.md` | 제품 방향 & 충돌 중재 & 범위 통제 |
| Backend Agent | `agents/backend/CLAUDE.md` | 백엔드 구현/수정 |
| Frontend Agent | `agents/frontend/CLAUDE.md` | 프론트엔드 구현/수정 |
| Reviewer Agent | `agents/reviewer/CLAUDE.md` | 코드 리뷰 & 디베이트 |
| QA Agent | `agents/qa/CLAUDE.md` | 최종 검증 |

---

## 지금 해야 할 일: 버그 수정 디베이트 사이클

### Round 0 — PM 우선순위 확인

Task 툴로 PM Agent spawn:
```
agents/pm/CLAUDE.md를 읽어라.
agents/qa/bug-report.md의 16개 버그를 검토하고:
1. 우선순위가 올바른지 PM 관점에서 확인해라
2. 특별히 주의해야 할 제품/법적 리스크를 지적해라
3. MVP 출시 기준에서 "지금 당장 필수 vs 다음 버전"을 판단해라
결과를 agents/pm/backlog.md에 정리해라.
```

### Round 1 — 백엔드 구현

Task 툴로 Backend Agent spawn:
```
agents/backend/CLAUDE.md를 읽고 아래 버그를 수정해라:
- agents/qa/bug-report.md의 BUG-001, 002, 003, 004, 009, 011, 015
수정 완료 후 변경된 파일 목록과 각 수정 내용을 상세히 보고해라.
```

### Round 2 — 프론트엔드 구현

Task 툴로 Frontend Agent spawn (백엔드와 병렬 가능):
```
agents/frontend/CLAUDE.md를 읽고 아래 버그를 수정해라:
- agents/qa/bug-report.md의 BUG-005, 006, 007, 010, 012, 013, 014, 016
수정 완료 후 변경된 파일 목록과 각 수정 내용을 상세히 보고해라.
```

### Round 3 — 리뷰어 디베이트

Task 툴로 Reviewer Agent spawn (백엔드 + 프론트엔드 결과물 전달):
```
agents/reviewer/CLAUDE.md를 읽어라.
Backend Agent와 Frontend Agent가 수정한 코드를 리뷰하고 다음을 수행해라:
1. 각 수정이 버그를 올바르게 해결했는지 검증
2. 새로운 버그나 부작용을 도입했는지 확인
3. 개선이 필요한 부분은 구체적인 수정 코드와 함께 지적해라
4. 문제없는 부분도 명시적으로 승인해라
반드시 비판적으로 검토해라 — 칭찬만 하는 리뷰는 무효다.
```

### Round 4 — PM 중재 (필요 시)

Reviewer와 구현 에이전트 간 의견 충돌이 있으면 PM Agent spawn:
```
agents/pm/CLAUDE.md를 읽어라.
Reviewer의 지적 사항과 구현 에이전트의 반박을 검토하고
PM 관점에서 최종 판단을 내려라.
```

### Round 4b — 수정 반영

PM/Reviewer 피드백 중 채택된 것을 Backend/Frontend Agent에 반영 지시.

### Round 5 — 최종 QA

Task 툴로 QA Agent spawn:
```
agents/qa/CLAUDE.md를 읽어라.
수정된 코드 전체를 정적 분석하고:
1. 16개 버그가 모두 수정됐는지 확인
2. 새로운 버그가 도입됐는지 확인
3. API 호환성 최종 검증
결과를 agents/qa/fix-report.md에 저장해라.
```

---

### Round 6 — PM 최종 승인

Task 툴로 PM Agent spawn:
```
agents/pm/CLAUDE.md를 읽어라.
agents/qa/fix-report.md를 검토하고:
1. 출시 가능 여부를 PM 관점에서 최종 판단해라
2. 남은 이슈 중 다음 버전으로 미룰 항목을 agents/pm/backlog.md에 공식 기록해라
3. SHIP / HOLD 판정을 내려라.
```

## 완료 보고

모든 작업 완료 후 반드시 실행:
```bash
openclaw system event --text "StockMind 디베이트 사이클 완료: 버그 16건 수정 검증 완료" --mode now
```
