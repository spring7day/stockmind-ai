"""
StockMind AI — FastAPI 메인 엔트리포인트
"""
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import stocks, watchlist


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행되는 이벤트 핸들러"""
    # 시작 시: Redis 연결 등 초기화
    from app.services.cache import cache_service
    await cache_service.connect()
    # 종목 목록 캐시 초기화
    from app.services import data_collector
    await data_collector.load_stock_list()
    print(f"[StockMind] 서버 시작 — 환경: {settings.APP_ENV}")
    yield
    # 종료 시: 연결 정리
    await cache_service.disconnect()
    print("[StockMind] 서버 종료")


app = FastAPI(
    title="StockMind AI API",
    description="AI 기반 한국 주식 심층 분석 서비스 API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS 설정 — Next.js 프론트엔드 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(stocks.router, prefix="/api/stocks", tags=["stocks"])
app.include_router(watchlist.router, prefix="/api/watchlist", tags=["watchlist"])


@app.get("/health", tags=["system"])
async def health_check():
    """서버 상태 확인 엔드포인트"""
    from app.services.cache import cache_service

    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
        "environment": settings.APP_ENV,
        "cache": await cache_service.ping(),
    }


@app.get("/", tags=["system"])
async def root():
    """루트 엔드포인트"""
    return {
        "service": "StockMind AI API",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
    )
