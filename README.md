# StockMind AI 🧠📈

> AI가 전문 애널리스트처럼 분석해주는 주식 컨설팅 서비스

## 빠른 시작 (개발)

```bash
cd projects/stockmind

# Claude Code Agent Teams 실행 (팀 리더 시작)
claude --dangerously-skip-permissions
```

## 프로젝트 구조

```
stockmind/
├── CLAUDE.md              # 팀 리더 지시사항
├── .claude/settings.json  # Agent Teams 설정
├── docs/
│   ├── PRD.md             # 제품 요구사항 문서
│   ├── SPRINT.md          # 스프린트 태스크 (PM Agent 관리)
│   └── USER_STORIES.md    # 유저 스토리
├── agents/
│   ├── pm/CLAUDE.md       # PM Agent
│   ├── ux/CLAUDE.md       # UX Agent + 와이어프레임
│   ├── infra/CLAUDE.md    # Infra Agent
│   └── qa/CLAUDE.md       # QA Agent
└── src/
    ├── frontend/          # Next.js 프론트엔드
    ├── backend/           # FastAPI 백엔드
    └── ai/                # AI 분석 엔진
```

## 에이전트 팀

| 에이전트 | 역할 |
|---|---|
| 🎯 PM | 요구사항, PRD, 우선순위 |
| 🎨 UX | 디자인, 와이어프레임 |
| ⚡ Frontend | Next.js UI |
| 🔧 Backend | FastAPI + 데이터 수집 |
| 🤖 AI/ML | 분석 엔진 + 프롬프트 |
| ☁️ Infra | 배포, CI/CD |
| ✅ QA | 테스트, 품질 |

## 제품 오너
지민님 — 요구사항 제공, 최종 의사결정
