"""
StockMind AI — 환경변수 및 설정 관리
pydantic-settings를 사용하여 .env 파일에서 자동 로드
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 서버 설정
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = True

    # CORS — 문자열로 받아 리스트로 변환
    ALLOWED_ORIGINS_STR: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS_STR.split(",")]

    # API 키
    ANTHROPIC_API_KEY: str = ""
    DART_API_KEY: str = ""
    ALPHA_VANTAGE_API_KEY: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # 캐시 TTL (초)
    CACHE_TTL_STOCK_INFO: int = 300
    CACHE_TTL_ANALYSIS: int = 3600
    CACHE_TTL_NEWS: int = 600
    CACHE_TTL_SIGNALS: int = 1800

    # OpenDART API 베이스 URL
    DART_BASE_URL: str = "https://opendart.fss.or.kr/api"


@lru_cache()
def get_settings() -> Settings:
    """설정 싱글턴 반환 (앱 전체에서 공유)"""
    return Settings()


# 전역 설정 인스턴스
settings = get_settings()
