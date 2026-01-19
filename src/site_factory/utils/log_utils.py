# v0.1 - 로거 설정 유틸 추가 (2026-01-16)
# 기능: 일관된 로그 포맷 제공 (예: create_logger("site_factory"))

import logging
from pathlib import Path
from typing import Optional

from .error_utils import FriendlyError


def create_logger(
    logger_name: str,
    level_text: str = "INFO",
    log_file_path: Optional[str] = None,
) -> logging.Logger:
    """로거를 생성한다. 예: create_logger("site_factory", level_text="DEBUG")"""

    # 로거 중복 핸들러 등록을 방지한다.
    logger = logging.getLogger(logger_name)
    if logger.handlers:
        return logger

    log_level = getattr(logging, level_text.upper(), logging.INFO)
    logger.setLevel(log_level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file_path:
        try:
            log_path = Path(log_file_path)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_path, encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except OSError as error:
            # 파일 로그가 실패해도 콘솔 로그는 유지한다.
            raise FriendlyError(
                user_message="로그 파일을 생성할 수 없습니다.",
                detail=str(error),
            ) from error

    return logger
