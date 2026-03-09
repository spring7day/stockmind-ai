"""
StockMind AI — 공통 API 응답 래퍼 모델
모든 엔드포인트 응답을 {success, data} 구조로 통일합니다.
"""
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """공통 API 응답 래퍼.

    성공: {"success": true, "data": <T>}
    실패: {"success": false, "error": "에러 메시지"}
    """

    success: bool = True
    data: Optional[T] = None
    error: Optional[str] = None

    @classmethod
    def ok(cls, data: T) -> "ApiResponse[T]":
        """성공 응답을 생성합니다."""
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, error: str) -> "ApiResponse[None]":
        """실패 응답을 생성합니다."""
        return cls(success=False, error=error)
