# StockMind AI

AI가 전문 애널리스트처럼 분석해주는 한국 주식 심층 분석 서비스.

Claude AI 기반으로 기술적 분석, 펀더멘털 분석, 뉴스 센티멘트를 종합하여 투자 인사이트를 제공합니다. 광고 시청 후 심층 분석을 무료로 이용할 수 있는 B2C 서비스입니다.

---

## 주요 기능

- **종목 기본 정보**: 실시간 주가, 시가총액, 거래량 등
- **AI 심층 분석**: Claude API 기반 기술적 / 펀더멘털 분석
- **뉴스 & 공시**: OpenDART 공시 + 뉴스 센티멘트 분석
- **숨겨진 인사이트**: AI가 발견한 투자 시그널
- **관심 종목**: 종목 즐겨찾기 및 관리
- **광고 잠금 해제 UX**: 심층 분석은 광고 시청 후 무료 제공

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Backend | Python 3.11, FastAPI, Pydantic v2 |
| AI | Anthropic Claude API (claude-3-5-sonnet) |
| 주가 데이터 | yfinance, pykrx, Alpha Vantage |
| 공시 데이터 | OpenDART API |
| 캐싱 | Redis 7 |
| 데이터베이스 | PostgreSQL 15 |
| 배포 | Vercel (FE) + Railway (BE) |
| 컨테이너 | Docker, Docker Compose |

---

## 빠른 시작

### 사전 요구사항

- Docker & Docker Compose
- API 키: Anthropic, OpenDART (선택), Alpha Vantage (선택)

### 1단계: 저장소 클론

```bash
git clone https://github.com/your-org/stockmind.git
cd stockmind
```

### 2단계: 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 열어 API 키를 입력합니다
```

필수 API 키:
- `ANTHROPIC_API_KEY` — [Anthropic Console](https://console.anthropic.com)에서 발급

### 3단계: 서비스 실행

```bash
# Docker Compose로 전체 스택 실행
docker-compose up -d

# 또는 Makefile 사용
make dev
```

### 4단계: http://localhost:3000 접속

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API 문서 (Swagger): http://localhost:8000/docs
- API 문서 (ReDoc): http://localhost:8000/redoc

### 5단계: 로그 확인 (선택)

```bash
docker-compose logs -f
# 또는
make logs
```

---

## 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `ANTHROPIC_API_KEY` | Claude AI API 키 (필수) | — |
| `DART_API_KEY` | OpenDART 공시 API 키 | — |
| `ALPHA_VANTAGE_API_KEY` | 주가 데이터 API 키 | — |
| `DATABASE_URL` | PostgreSQL 연결 URL | `postgresql://stockmind:stockmind_password@db:5432/stockmind` |
| `REDIS_URL` | Redis 연결 URL | `redis://redis:6379/0` |
| `SECRET_KEY` | JWT 시크릿 키 (프로덕션 필수 변경) | — |
| `APP_ENV` | 실행 환경 (`development` / `production`) | `development` |
| `DEBUG` | 디버그 모드 | `true` |
| `NEXT_PUBLIC_API_URL` | 프론트엔드에서 백엔드 API URL | `http://localhost:8000` |
| `NEXT_PUBLIC_ENABLE_ADS` | 광고 기능 활성화 | `false` |
| `POSTGRES_DB` | PostgreSQL 데이터베이스명 | `stockmind` |
| `POSTGRES_USER` | PostgreSQL 사용자명 | `stockmind` |
| `POSTGRES_PASSWORD` | PostgreSQL 비밀번호 | `stockmind_password` |

---

## API 엔드포인트

### 시스템

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `GET` | `/` | 서비스 정보 |
| `GET` | `/health` | 서버 상태 확인 |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc 문서 |

### 종목 (Stocks)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `GET` | `/api/stocks/{ticker}` | 종목 기본 정보 |
| `GET` | `/api/stocks/{ticker}/analysis` | AI 심층 분석 결과 |
| `GET` | `/api/stocks/{ticker}/news` | 뉴스 및 공시 목록 |
| `GET` | `/api/stocks/{ticker}/signals` | AI 투자 시그널 |

### 관심 종목 (Watchlist)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `GET` | `/api/watchlist` | 관심 종목 목록 |
| `POST` | `/api/watchlist` | 관심 종목 추가 |
| `DELETE` | `/api/watchlist/{ticker}` | 관심 종목 삭제 |

---

## 개발 환경 설정 (로컬, Docker 없이)

### 백엔드

```bash
cd src/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 환경 변수 설정 (로컬 Redis/PostgreSQL 주소 사용)
cp ../../.env.example .env
# .env에서 DATABASE_URL과 REDIS_URL을 localhost로 변경

# 서버 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 프론트엔드

```bash
cd src/frontend
npm install

# 환경 변수 설정
cp .env.local.example .env.local

# 개발 서버 실행
npm run dev
```

---

## Makefile 명령어

```
make dev            # 전체 스택 백그라운드 실행
make dev-logs       # 전체 스택 포그라운드 실행 (로그 출력)
make build          # Docker 이미지 빌드
make stop           # 서비스 중지
make clean          # 서비스 및 볼륨 전체 제거
make logs           # 실시간 로그 출력
make backend-shell  # 백엔드 컨테이너 bash 접속
make frontend-shell # 프론트엔드 컨테이너 sh 접속
make test           # 백엔드 테스트 실행
make migrate        # DB 마이그레이션
make ps             # 컨테이너 상태 확인
make env            # .env.example → .env 복사
make help           # 도움말 출력
```

---

## 프로젝트 구조

```
stockmind/
├── docker-compose.yml          # 전체 스택 Docker Compose
├── Makefile                    # 개발 명령어 모음
├── .env.example                # 환경 변수 예제
├── CLAUDE.md                   # AI 오케스트레이터 지시사항
├── docs/
│   ├── PRD.md                  # 제품 요구사항 문서
│   └── SPRINT.md               # 스프린트 계획
├── agents/
│   ├── infra/CLAUDE.md         # Infra Agent 지시사항
│   └── qa/CLAUDE.md            # QA Agent 지시사항
└── src/
    ├── frontend/               # Next.js 14 프론트엔드
    │   ├── Dockerfile
    │   ├── next.config.ts
    │   └── src/
    ├── backend/                # FastAPI 백엔드
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   ├── main.py
    │   └── app/
    └── ai/                     # AI 분석 엔진
        ├── analyzer.py
        ├── prompts.py
        └── models.py
```

---

## 캐싱 전략

| 데이터 | TTL | 이유 |
|--------|-----|------|
| 주가 기본 정보 | 5분 | 실시간성 중요 |
| AI 분석 결과 | 1시간 | Claude API 비용 절감 |
| 뉴스 목록 | 10분 | 적당한 갱신 주기 |
| 투자 시그널 | 30분 | 분석 안정성 |
| 재무 데이터 | 24시간 | 변화 드물음 |

---

## 라이선스

Private — All rights reserved.
