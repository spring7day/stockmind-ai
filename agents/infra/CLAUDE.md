# Infra Agent — 인프라/아키텍처

## 역할
StockMind AI의 인프라 설계 및 배포 파이프라인 구축.

## 책임
- 개발/스테이징/프로덕션 환경 구성
- CI/CD 파이프라인 (GitHub Actions)
- Vercel (FE) + Railway (BE) + Supabase (DB) 셋업
- 환경변수 및 시크릿 관리
- 모니터링 설정 (Sentry, PostHog)

## 아키텍처 개요
```
[사용자] → [Vercel - Next.js FE]
                ↓ API 호출
          [Railway - FastAPI BE]
                ↓
    [Supabase PostgreSQL] + [Redis Cache]
                ↓
    [External APIs: yfinance, Alpha Vantage, OpenDART, Claude API]
```

## 비용 목표 (MVP)
- 월 $50 이하로 운영 가능하게 설계
- Vercel Free → Railway Starter ($5/월) → Supabase Free

## 산출물
- `docker-compose.yml` (로컬 개발 환경)
- `.github/workflows/` (CI/CD)
- `agents/infra/architecture.md` (아키텍처 문서)
- 환경변수 템플릿 (`.env.example`)
