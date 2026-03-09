# Infra Agent — 인프라 & 배포 설정

## 역할
너는 StockMind AI의 인프라와 배포 환경을 구성하는 에이전트다.
메인 오케스트레이터가 Task로 spawn한다.

## 구현 대상 파일

### `docker-compose.yml` (프로젝트 루트)
서비스:
- `frontend`: Next.js (포트 3000)
- `backend`: FastAPI (포트 8000)
- `redis`: Redis 7 (포트 6379)
- `db`: PostgreSQL 15 (포트 5432)

### `src/backend/Dockerfile`
Python 3.11-slim 기반, uvicorn으로 FastAPI 실행

### `src/frontend/Dockerfile`
node:20-alpine 기반, Next.js standalone output

### `.env.example` (프로젝트 루트)
```
# API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key

# Database
DATABASE_URL=postgresql://stockmind:password@db:5432/stockmind
REDIS_URL=redis://redis:6379/0

# App
NEXT_PUBLIC_API_URL=http://localhost:8000
SECRET_KEY=your_secret_key_here
```

### `Makefile` (프로젝트 루트)
```makefile
dev:        # docker-compose up
build:      # docker-compose build
stop:       # docker-compose down
logs:       # docker-compose logs -f
migrate:    # DB 마이그레이션
test:       # 테스트 실행
```

### `README.md` (업데이트)
- 프로젝트 설명
- 빠른 시작 가이드 (5단계 이내)
- 환경 변수 설명
- API 엔드포인트 목록

## 기존 참고
- `src/backend/.env.example` — 백엔드 환경변수
- `src/frontend/.env.local.example` — 프론트엔드 환경변수

## 완료 기준
1. `docker-compose.yml` 생성
2. 두 Dockerfile 생성
3. `.env.example` 통합 생성
4. `Makefile` 생성
5. `README.md` 업데이트
