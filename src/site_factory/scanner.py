# v0.1 - Elementor 스캐너 초기 구현 (2026-01-19)
# 기능: Elementor JSON에서 주입 후보를 추출하고 어댑터 스켈레톤을 생성

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from .utils.error_utils import FriendlyError
from .utils.io_utils import read_json_file, write_json_file, ensure_directory
from .utils.time_utils import get_iso_timestamp


@dataclass(frozen=True)
class ScanOptions:
    """스캐너 옵션. 예: ScanOptions(page_slug="home", max_candidates=200)"""

    page_slug: str
    template_id: str
    max_candidates: int
    max_depth: int


def scan_elementor_json(
    *,
    input_path: Path,
    output_dir: Path,
    page_slug: str,
    template_id: str = "unknown",
    max_candidates: int = 300,
    max_depth: int = 12,
) -> Dict[str, Any]:
    """Elementor JSON을 스캔한다. 예: scan_elementor_json(input_path=..., output_dir=...)"""

    try:
        elementor_data = read_json_file(input_path)
    except FriendlyError:
        raise
    except Exception as error:
        raise FriendlyError(
            user_message=f"Elementor JSON을 읽을 수 없습니다: {input_path}",
            detail=str(error),
        ) from error

    elements_root = _extract_elements_root(elementor_data)
    if not elements_root:
        raise FriendlyError(
            user_message="Elementor JSON에서 elements 루트를 찾을 수 없습니다."
        )

    options = ScanOptions(
        page_slug=page_slug,
        template_id=template_id,
        max_candidates=max_candidates,
        max_depth=max_depth,
    )

    candidates, stats = _collect_candidates(elements_root, options)

    manifest = _build_manifest(
        input_path=input_path,
        options=options,
        candidates=candidates,
        stats=stats,
    )
    adapter_skeleton = _build_adapter_skeleton(options, candidates)

    output_root = ensure_directory(output_dir)
    manifest_path = output_root / "manifest.json"
    adapter_path = output_root / "adapter_skeleton.json"

    write_json_file(manifest_path, manifest)
    write_json_file(adapter_path, adapter_skeleton)

    return {
        "manifest_path": str(manifest_path),
        "adapter_skeleton_path": str(adapter_path),
        "candidate_count": len(candidates),
        "stats": stats,
    }


def _extract_elements_root(data: Any) -> List[Dict[str, Any]]:
    """Elementor JSON의 elements 루트를 찾는다. 예: _extract_elements_root(data)"""

    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]

    if isinstance(data, dict):
        elements = data.get("elements")
        if isinstance(elements, list):
            return [item for item in elements if isinstance(item, dict)]

        # 일부 JSON은 다른 키에 elements가 포함될 수 있으므로 얕은 탐색만 수행한다.
        for value in data.values():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                if _looks_like_element_list(value):
                    return value

    return []


def _looks_like_element_list(value: List[Any]) -> bool:
    """Elementor elements 리스트인지 추정한다. 예: _looks_like_element_list(elements)"""

    for item in value[:5]:
        if not isinstance(item, dict):
            return False
        if "id" not in item or "elements" not in item:
            return False
    return True


def _collect_candidates(
    elements_root: List[Dict[str, Any]],
    options: ScanOptions,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """후보를 수집한다. 예: candidates, stats = _collect_candidates(elements_root, options)"""

    candidates: List[Dict[str, Any]] = []
    seen: Set[Tuple[str, str]] = set()
    stats = {
        "element_count": 0,
        "candidate_limit_reached": False,
        "skipped_text": 0,
    }

    for element in _walk_elements(elements_root, depth=0, max_depth=options.max_depth):
        stats["element_count"] += 1

        element_id = element.get("id")
        settings = element.get("settings", {})
        widget_type = element.get("widgetType") or element.get("widget_type")
        css_id = _extract_css_id(settings)

        if not isinstance(settings, dict):
            continue

        extracted = _extract_candidates_from_settings(
            settings=settings,
            element_id=element_id,
            widget_type=widget_type,
            css_id=css_id,
            stats=stats,
        )

        for item in extracted:
            candidate_key = (item["element_id"], item["path"])
            if candidate_key in seen:
                continue
            seen.add(candidate_key)
            candidates.append(item)

            if len(candidates) >= options.max_candidates:
                stats["candidate_limit_reached"] = True
                return candidates, stats

    return candidates, stats


def _walk_elements(
    elements: List[Dict[str, Any]],
    depth: int,
    max_depth: int,
) -> Iterable[Dict[str, Any]]:
    """Elementor elements 트리를 순회한다. 예: for el in _walk_elements(elements, 0, 10)"""

    if depth > max_depth:
        return

    for element in elements:
        if not isinstance(element, dict):
            continue
        yield element

        children = element.get("elements", [])
        if isinstance(children, list):
            yield from _walk_elements(children, depth + 1, max_depth)


def _extract_candidates_from_settings(
    *,
    settings: Dict[str, Any],
    element_id: Optional[str],
    widget_type: Optional[str],
    css_id: Optional[str],
    stats: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """settings에서 후보를 추출한다. 예: _extract_candidates_from_settings(settings=..., ...)"""

    if not element_id:
        return []

    candidates: List[Dict[str, Any]] = []

    for key, value in settings.items():
        if _is_ignored_setting_key(key):
            continue

        base_path = f"settings.{key}"
        candidates.extend(
            _extract_candidates_from_value(
                value=value,
                element_id=element_id,
                widget_type=widget_type,
                css_id=css_id,
                base_path=base_path,
                key_name=key,
                stats=stats,
            )
        )

    return candidates


def _extract_candidates_from_value(
    *,
    value: Any,
    element_id: str,
    widget_type: Optional[str],
    css_id: Optional[str],
    base_path: str,
    key_name: str,
    stats: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """settings의 값에서 후보를 뽑는다. 예: _extract_candidates_from_value(value=..., ...)"""

    candidates: List[Dict[str, Any]] = []

    if isinstance(value, str):
        field_type = _infer_field_type(key_name, value)
        if not field_type:
            stats["skipped_text"] += 1
            return []
        candidates.append(
            _build_candidate(
                element_id=element_id,
                widget_type=widget_type,
                css_id=css_id,
                field_type=field_type,
                path=base_path,
                preview=value,
            )
        )
        return candidates

    if isinstance(value, dict):
        # url이 있는 경우 링크/이미지 후보로 간주한다.
        url_value = value.get("url")
        if isinstance(url_value, str) and url_value:
            field_type = _infer_field_type(key_name, url_value, assume_url=True)
            candidates.append(
                _build_candidate(
                    element_id=element_id,
                    widget_type=widget_type,
                    css_id=css_id,
                    field_type=field_type,
                    path=f"{base_path}.url",
                    preview=url_value,
                )
            )
        return candidates

    if isinstance(value, list):
        for index, item in enumerate(value):
            if not isinstance(item, dict):
                continue
            for sub_key, sub_value in item.items():
                if not isinstance(sub_value, str):
                    continue
                field_type = _infer_field_type(sub_key, sub_value)
                if not field_type:
                    continue
                candidates.append(
                    _build_candidate(
                        element_id=element_id,
                        widget_type=widget_type,
                        css_id=css_id,
                        field_type=field_type,
                        path=f"{base_path}.{index}.{sub_key}",
                        preview=sub_value,
                    )
                )
        return candidates

    return candidates


def _infer_field_type(
    key_name: str,
    value: str,
    assume_url: bool = False,
) -> Optional[str]:
    """필드 타입을 추정한다. 예: _infer_field_type("title", "Hello")"""

    normalized_key = key_name.lower()
    normalized_value = value.strip()

    if not normalized_value:
        return None

    if _looks_like_color(normalized_value):
        return None

    if assume_url or _looks_like_url(normalized_value):
        if "image" in normalized_key or "bg" in normalized_key:
            return "image"
        return "link"

    if "url" in normalized_key or "link" in normalized_key:
        return "link"

    # 텍스트 후보 키워드를 우선 적용한다.
    text_keywords = ("title", "text", "desc", "content", "editor", "heading", "label")
    if any(keyword in normalized_key for keyword in text_keywords):
        return "text"

    # 기본은 텍스트로 처리하되 너무 짧은 값은 제외한다.
    if len(normalized_value) < 3:
        return None

    return "text"


def _build_candidate(
    *,
    element_id: str,
    widget_type: Optional[str],
    css_id: Optional[str],
    field_type: str,
    path: str,
    preview: str,
) -> Dict[str, Any]:
    """후보 레코드를 만든다. 예: _build_candidate(...)"""

    trimmed_preview = preview.strip()
    if len(trimmed_preview) > 120:
        trimmed_preview = f"{trimmed_preview[:117]}..."

    return {
        "element_id": element_id,
        "css_id": css_id,
        "widget_type": widget_type,
        "field_type": field_type,
        "path": path,
        "preview": trimmed_preview,
    }


def _build_manifest(
    *,
    input_path: Path,
    options: ScanOptions,
    candidates: List[Dict[str, Any]],
    stats: Dict[str, Any],
) -> Dict[str, Any]:
    """manifest.json을 생성한다. 예: _build_manifest(input_path=..., ...)"""

    return {
        "source_file": str(input_path),
        "generated_at": get_iso_timestamp(),
        "template_id": options.template_id,
        "page_slug": options.page_slug,
        "stats": stats,
        "candidates": candidates,
    }


def _build_adapter_skeleton(
    options: ScanOptions,
    candidates: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """adapter_skeleton.json을 만든다. 예: _build_adapter_skeleton(options, candidates)"""

    patches: List[Dict[str, Any]] = []
    for index, candidate in enumerate(candidates, start=1):
        op = _map_field_type_to_op(candidate["field_type"])
        patches.append(
            {
                "key": f"TODO.value_{index}",
                "element_id": candidate["element_id"],
                "path": candidate["path"],
                "op": op,
            }
        )

    return {
        "template_id": options.template_id,
        "pages": [
            {
                "post_slug": options.page_slug,
                "patches": patches,
            }
        ],
        "globals": {},
        "notes": "TODO: key 값을 site_spec 경로로 교체하세요.",
    }


def _map_field_type_to_op(field_type: str) -> str:
    """field_type을 op로 변환한다. 예: _map_field_type_to_op("text")"""

    if field_type == "image":
        return "set_image_url"
    if field_type == "link":
        return "set_url"
    return "set_text"


def _extract_css_id(settings: Dict[str, Any]) -> Optional[str]:
    """settings에서 CSS ID를 추출한다. 예: _extract_css_id(settings)"""

    for key in ("_css_id", "css_id", "cssId", "cssid"):
        value = settings.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _is_ignored_setting_key(key_name: str) -> bool:
    """무시할 settings 키인지 확인한다. 예: _is_ignored_setting_key("_css_id")"""

    ignored_keys = {
        "_css_id",
        "css_id",
        "cssId",
        "cssid",
        "_element_id",
        "_custom_css",
        "custom_css",
        "css_classes",
        "css_class",
        "classes",
        "class",
    }
    return key_name in ignored_keys


def _looks_like_url(value: str) -> bool:
    """URL 형태인지 간단히 판단한다. 예: _looks_like_url("https://...")"""

    return value.startswith(("http://", "https://", "//")) or "." in value and "/" in value


def _looks_like_color(value: str) -> bool:
    """컬러 코드 형태인지 판단한다. 예: _looks_like_color("#ffffff")"""

    if not value.startswith("#"):
        return False
    hex_digits = value[1:]
    return len(hex_digits) in (3, 6, 8) and all(char in "0123456789abcdefABCDEF" for char in hex_digits)
