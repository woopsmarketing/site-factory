# v0.1 - 친절한 에러 처리 유틸 추가 (2026-01-16)
# 기능: 사용자 친화적 예외를 표준화 (예: raise FriendlyError("설정 파일이 없습니다"))

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class FriendlyError(Exception):
    """사용자에게 보여줄 메시지를 담는 예외. 예: raise FriendlyError("입력 파일이 없습니다")"""

    user_message: str
    detail: Optional[str] = None

    def __str__(self) -> str:
        # 사용자 메시지를 기본 문자열로 반환한다.
        return self.user_message


def build_user_friendly_message(error: Exception) -> str:
    """예상치 못한 에러를 사용자 친화적 문구로 변환한다. 예: build_user_friendly_message(exc)"""

    # 예외 타입별로 메시지를 정리해 노출한다.
    if isinstance(error, FriendlyError):
        return error.user_message

    return "예상치 못한 오류가 발생했습니다. 로그를 확인해주세요."
