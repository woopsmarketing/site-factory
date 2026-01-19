# v0.2 - 리스트 인덱스 경로 지원 추가 (2026-01-19)
# 기능: 중첩 키 조회/설정 (예: get_nested_value(data, "settings.items.0.text"))

from typing import Any, Dict, Iterable, Optional

_MISSING = object()


def get_nested_value(
    data: Dict[str, Any],
    key_path: str,
    default: Optional[Any] = None,
    separator: str = ".",
) -> Any:
    """중첩 키를 안전하게 조회한다. 예: get_nested_value(site_spec, "brand.name")"""

    if not key_path:
        return default

    current: Any = data
    for key in _split_path(key_path, separator):
        # 딕셔너리 경로 처리
        if isinstance(current, dict) and key in current:
            current = current[key]
            continue

        # 리스트 인덱스 처리
        if isinstance(current, list) and key.isdigit():
            index = int(key)
            if 0 <= index < len(current):
                current = current[index]
                continue

        return default
    return current


def has_nested_value(
    data: Dict[str, Any],
    key_path: str,
    separator: str = ".",
) -> bool:
    """중첩 키의 존재 여부를 확인한다. 예: has_nested_value(site_spec, "seo.home.title")"""

    return get_nested_value(data, key_path, default=_MISSING, separator=separator) is not _MISSING


def set_nested_value(
    data: Dict[str, Any],
    key_path: str,
    value: Any,
    separator: str = ".",
    strict: bool = True,
) -> bool:
    """중첩 키 값을 설정한다. 예: set_nested_value(element, "settings.title", "새 제목")"""

    if not key_path:
        return False

    keys = list(_split_path(key_path, separator))
    current: Any = data

    # 중간 경로를 따라간다. dict 또는 list 인덱스를 허용한다.
    for key in keys[:-1]:
        if isinstance(current, dict) and key in current:
            current = current[key]
            continue

        if isinstance(current, list) and key.isdigit():
            index = int(key)
            if 0 <= index < len(current):
                current = current[index]
                continue
            return False

        if strict:
            return False

        if isinstance(current, dict):
            current[key] = {}
            current = current[key]
            continue

        return False

    last_key = keys[-1]
    if isinstance(current, dict):
        current[last_key] = value
        return True

    if isinstance(current, list) and last_key.isdigit():
        index = int(last_key)
        if 0 <= index < len(current):
            current[index] = value
            return True

    return False


def _split_path(key_path: str, separator: str) -> Iterable[str]:
    """경로 문자열을 분할한다. 예: list(_split_path("a.b.c", "."))"""

    return (segment for segment in key_path.split(separator) if segment)
