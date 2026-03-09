"""
StockMind AI — Redis 캐시 서비스
Redis가 없으면 in-memory 딕셔너리로 폴백합니다.
"""
import json
import logging
import time
from typing import Any, Optional

logger = logging.getLogger(__name__)


class CacheService:
    """
    Redis 우선, 없으면 in-memory 캐시로 폴백하는 캐시 서비스.
    애플리케이션 전체에서 싱글턴으로 사용합니다.
    """

    def __init__(self):
        self._redis = None
        self._memory: dict[str, tuple[Any, float]] = {}  # {key: (value, expires_at)}
        self._use_redis = False

    async def connect(self):
        """Redis에 연결을 시도합니다. 실패하면 in-memory 모드로 전환합니다."""
        from app.config import settings

        try:
            import redis.asyncio as aioredis

            self._redis = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=3,
                socket_timeout=3,
            )
            # 연결 테스트
            await self._redis.ping()
            self._use_redis = True
            logger.info(f"Redis 연결 성공: {settings.REDIS_URL}")
        except Exception as e:
            logger.warning(f"Redis 연결 실패 ({e}) — in-memory 캐시로 폴백합니다.")
            self._redis = None
            self._use_redis = False

    async def disconnect(self):
        """Redis 연결을 종료합니다."""
        if self._redis:
            try:
                await self._redis.close()
            except Exception:
                pass
        self._redis = None
        self._use_redis = False

    async def ping(self) -> str:
        """캐시 서비스 상태를 반환합니다."""
        if self._use_redis and self._redis:
            try:
                await self._redis.ping()
                return "redis:ok"
            except Exception:
                return "redis:error"
        return "memory:ok"

    async def get(self, key: str) -> Optional[Any]:
        """
        캐시에서 값을 조회합니다.
        JSON으로 직렬화된 값을 역직렬화하여 반환합니다.
        """
        if self._use_redis and self._redis:
            try:
                raw = await self._redis.get(key)
                if raw is None:
                    return None
                return json.loads(raw)
            except Exception as e:
                logger.error(f"Redis GET 오류 ({key}): {e}")
                return None
        else:
            # in-memory 캐시
            entry = self._memory.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if expires_at > 0 and time.time() > expires_at:
                del self._memory[key]
                return None
            return value

    async def set(self, key: str, value: Any, ttl: int = 300):
        """
        캐시에 값을 저장합니다.
        ttl: 만료 시간 (초). 0이면 만료 없음.
        """
        if self._use_redis and self._redis:
            try:
                serialized = json.dumps(value, ensure_ascii=False, default=str)
                if ttl > 0:
                    await self._redis.setex(key, ttl, serialized)
                else:
                    await self._redis.set(key, serialized)
            except Exception as e:
                logger.error(f"Redis SET 오류 ({key}): {e}")
        else:
            # in-memory 캐시
            expires_at = (time.time() + ttl) if ttl > 0 else 0
            self._memory[key] = (value, expires_at)

    async def delete(self, key: str):
        """캐시에서 키를 삭제합니다."""
        if self._use_redis and self._redis:
            try:
                await self._redis.delete(key)
            except Exception as e:
                logger.error(f"Redis DELETE 오류 ({key}): {e}")
        else:
            self._memory.pop(key, None)

    async def delete_pattern(self, pattern: str):
        """패턴에 매칭되는 키를 모두 삭제합니다. (예: 'stock:005930:*')"""
        if self._use_redis and self._redis:
            try:
                keys = await self._redis.keys(pattern)
                if keys:
                    await self._redis.delete(*keys)
            except Exception as e:
                logger.error(f"Redis DELETE PATTERN 오류 ({pattern}): {e}")
        else:
            # in-memory: 단순 prefix 매칭
            prefix = pattern.rstrip("*")
            keys_to_delete = [k for k in self._memory if k.startswith(prefix)]
            for k in keys_to_delete:
                del self._memory[k]

    def _clean_expired(self):
        """만료된 in-memory 캐시 항목을 정리합니다."""
        now = time.time()
        expired = [k for k, (_, exp) in self._memory.items() if exp > 0 and now > exp]
        for k in expired:
            del self._memory[k]


# 전역 싱글턴 인스턴스
cache_service = CacheService()


# ────────────────────────────────────────────────
# 캐시 키 헬퍼
# ────────────────────────────────────────────────

def cache_key_stock_info(ticker: str) -> str:
    return f"stock:{ticker}:info"


def cache_key_analysis(ticker: str) -> str:
    return f"stock:{ticker}:analysis"


def cache_key_news(ticker: str) -> str:
    return f"stock:{ticker}:news"


def cache_key_signals(ticker: str) -> str:
    return f"stock:{ticker}:signals"


def cache_key_search(query: str) -> str:
    return f"search:{query.lower()}"
