# StockMind AI — 메인 오케스트레이터

> 너는 StockMind AI 프로젝트의 **메인 오케스트레이터**다.
> Claude Code의 `Task` 툴을 사용해 서브에이전트를 직접 spawn하고, 결과를 검증한 뒤 계속 반복한다.
> Jarvis(상위 에이전트)는 너만 실행한다. 나머지는 네가 직접 조율한다.

---

## 프로젝트 개요

**서비스명:** StockMind AI  
**목적:** AI 기반 주식 종목 심층 분석 웹 서비스 (B2C, 광고 수익 모델)  
**PRD:** `docs/PRD.md` 참고  
**현재 워크디렉토리:** `/Users/jimin/.openclaw/workspace/projects/stockmind`

---

## 현재 상태 (2026-03-09)

### ✅ 완료된 것
- `src/backend/` — FastAPI 백엔드 (routers, services, models)
- `src/frontend/` — Next.js 14 프론트엔드 (components, pages, AdGate)

### 🔄 남은 작업
1. **AI 에이전트** (`src/ai/`) — Claude API 기반 종목 분석 엔진
2. **인프라** (`agents/infra/`) — Docker Compose, 배포 설정
3. **통합 테스트** — 백엔드↔프론트엔드 연결 검증
4. **최종 검증** — 전체 파이프라인 동작 확인

---

## 오케스트레이터 역할

너는 다음을 반복한다:

1. **현재 상태 파악** — 파일 트리, 코드 훑기
2. **Task 툴로 서브에이전트 spawn** — 각 역할별 CLAUDE.md 참고
3. **결과 검증** — 생성된 코드가 기존 코드와 호환되는지 확인
4. **필요시 수정 지시** — 문제 발견 시 다시 spawn해서 수정
5. **완료 보고** — 모든 작업 완료 시 아래 명령 실행

---

## 서브에이전트 역할 & CLAUDE.md 위치

| 역할 | CLAUDE.md 위치 | 담당 |
|------|--------------|------|
| AI/ML Agent | `src/ai/CLAUDE.md` | Claude API 분석 엔진 |
| Infra Agent | `agents/infra/CLAUDE.md` | Docker, 배포 설정 |
| QA Agent | `agents/qa/CLAUDE.md` | 테스트, 검증 |

---

## 지금 당장 해야 할 일

### Step 1: AI 분석 엔진 구현

`Task` 툴을 사용해 AI Agent를 spawn해서 다음을 구현:

```
작업: src/ai/ 디렉토리에 AI 분석 엔진 구현
참고: src/ai/CLAUDE.md
구현 내용:
- src/ai/__init__.py
- src/ai/analyzer.py (StockAnalyzer 클래스)
  - analyze_technical(ticker) → 기술적 분석
  - analyze_fundamental(ticker) → 펀더멘털 분석  
  - analyze_sentiment(ticker) → 뉴스 센티멘트
  - generate_insight(ticker) → 종합 AI 인사이트
- src/ai/prompts.py (Claude API 프롬프트 템플릿)
- src/ai/models.py (Pydantic 분석 결과 모델)
기존 백엔드: src/backend/app/services/ai_analyzer.py 참고해서 호환되게 구현
```

### Step 2: 백엔드 AI 서비스 연동

AI 엔진이 완성되면 `src/backend/app/services/ai_analyzer.py`를 실제로 동작하도록 업데이트.

### Step 3: Infra Agent spawn

Docker Compose + 환경 변수 설정.

### Step 4: 전체 검증

생성된 코드 전체를 훑어보고:
- import 오류 없는지
- API 호환성 확인
- 누락된 파일 없는지
발견된 문제는 해당 서브에이전트 다시 spawn해서 수정.

---

## 기술 스택

- Frontend: Next.js 14 + TypeScript + Tailwind CSS
- Backend: Python 3.11 + FastAPI
- AI: Anthropic Claude API (claude-3-5-sonnet 또는 claude-3-haiku)
- 데이터: yfinance, Alpha Vantage
- DB: PostgreSQL + Redis
- 배포: Vercel (FE) + Railway (BE)

---

## 개발 원칙

1. **기존 코드와 호환** — src/backend/, src/frontend/ 이미 만들어진 코드 구조 유지
2. **실제로 동작하는 코드** — 스텁(stub)이 아닌 실제 구현
3. **에러 핸들링** — 모든 외부 API 호출에 try/except
4. **타입 안전** — TypeScript strict, Python type hints 필수

---

## 완료 보고

모든 작업이 완료되면 반드시 실행:
```bash
openclaw system event --text "StockMind Teams 완료: AI엔진+인프라+검증 완료. src/ai/ 구현, Docker 설정, 통합 테스트 완료" --mode now
```
