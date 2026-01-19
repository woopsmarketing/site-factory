# v0.1 - 시간 유틸 추가 (2026-01-16)
# 기능: ISO 타임스탬프 생성 (예: get_iso_timestamp())

from datetime import datetime, timezone


def get_iso_timestamp() -> str:
    """UTC 기준 ISO 타임스탬프를 생성한다. 예: get_iso_timestamp()"""

    # 서버/로컬 시간 차이를 줄이기 위해 UTC로 고정한다.
    return datetime.now(timezone.utc).isoformat()
