# v0.1 - 파일 입출력 유틸 추가 (2026-01-16)
# 기능: JSON 읽기/쓰기와 디렉터리 보장 (예: read_json_file("data/mock/site_spec.sample.json"))

import json
from pathlib import Path
from typing import Any, Dict, Union

from .error_utils import FriendlyError

PathLike = Union[str, Path]


def ensure_directory(directory_path: PathLike) -> Path:
    """디렉터리를 생성/보장한다. 예: ensure_directory("output")"""

    try:
        normalized_path = Path(directory_path)
        normalized_path.mkdir(parents=True, exist_ok=True)
        return normalized_path
    except OSError as error:
        raise FriendlyError(
            user_message="디렉터리를 생성할 수 없습니다.",
            detail=str(error),
        ) from error


def read_json_file(file_path: PathLike) -> Dict[str, Any]:
    """JSON 파일을 읽는다. 예: read_json_file("data/mock/site_spec.sample.json")"""

    normalized_path = Path(file_path)

    if not normalized_path.exists():
        raise FriendlyError(
            user_message=f"JSON 파일을 찾을 수 없습니다: {normalized_path}",
        )

    try:
        with normalized_path.open("r", encoding="utf-8") as file_handle:
            return json.load(file_handle)
    except json.JSONDecodeError as error:
        raise FriendlyError(
            user_message=f"JSON 파싱에 실패했습니다: {normalized_path}",
            detail=str(error),
        ) from error
    except OSError as error:
        raise FriendlyError(
            user_message=f"JSON 파일을 읽을 수 없습니다: {normalized_path}",
            detail=str(error),
        ) from error


def write_json_file(file_path: PathLike, data: Dict[str, Any]) -> None:
    """JSON 파일을 저장한다. 예: write_json_file("output/result.json", data)"""

    normalized_path = Path(file_path)

    try:
        normalized_path.parent.mkdir(parents=True, exist_ok=True)
        with normalized_path.open("w", encoding="utf-8") as file_handle:
            json.dump(data, file_handle, ensure_ascii=False, indent=2)
    except OSError as error:
        raise FriendlyError(
            user_message=f"JSON 파일을 저장할 수 없습니다: {normalized_path}",
            detail=str(error),
        ) from error
