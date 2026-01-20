# v0.3 - 복합 위젯 op 처리/ CSS ID 매칭 개선 (2026-01-20)
# 기능: adapter patch를 Elementor JSON에 적용 (예: apply_patches_to_elementor(data, adapter, site_spec))

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .utils.dict_utils import get_nested_value, set_nested_value


def apply_patches_to_elementor(
    elementor_data: Dict[str, Any],
    adapter: Dict[str, Any],
    site_spec: Dict[str, Any],
    strict_path: bool = True,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """패치 목록을 적용한다. 예: patched, results = apply_patches_to_elementor(...)"""

    patched_data = deepcopy(elementor_data)
    patch_results: List[Dict[str, Any]] = []

    for page in adapter.get("pages", []):
        for patch in page.get("patches", []):
            result = _apply_single_patch(
                patched_data=patched_data,
                patch=patch,
                site_spec=site_spec,
                strict_path=strict_path,
            )
            patch_results.append(result)

    return patched_data, patch_results


def _apply_single_patch(
    patched_data: Dict[str, Any],
    patch: Dict[str, Any],
    site_spec: Dict[str, Any],
    strict_path: bool,
) -> Dict[str, Any]:
    """단일 패치를 적용한다. 예: _apply_single_patch(patched_data, patch, site_spec, True)"""

    element_id = patch.get("element_id")
    css_id = patch.get("css_id")
    op = patch.get("op")
    key_path = patch.get("key")
    target_path = patch.get("path")

    if not op or not key_path or not target_path or (not element_id and not css_id):
        return {
            "status": "error",
            "message": "patch 필수 필드가 누락되었습니다.",
            "patch": patch,
        }

    element_parent, element_index, element = _find_element(
        patched_data=patched_data,
        element_id=element_id,
        css_id=css_id,
    )
    if element is None:
        return {
            "status": "error",
            "message": f"요소를 찾을 수 없습니다: {element_id or css_id}",
            "patch": patch,
        }

    if op == "delete":
        # 삭제는 요소 자체를 리스트에서 제거한다.
        _remove_element_by_index(element_parent, element_index)
        return {
            "status": "deleted",
            "message": "요소를 삭제했습니다.",
            "patch": patch,
        }

    value = get_nested_value(site_spec, key_path)
    if value is None:
        return {
            "status": "skipped",
            "message": f"site_spec 값이 없어 건너뜁니다: {key_path}",
            "patch": patch,
        }

    # 한글: op별로 처리 방식이 다를 수 있어 분기한다.
    success = _apply_patch_value(
        element=element,
        target_path=target_path,
        value=value,
        op=op,
        strict_path=strict_path,
    )
    if not success:
        return {
            "status": "error",
            "message": f"경로 설정 실패: {target_path}",
            "patch": patch,
        }

    return {
        "status": "applied",
        "message": "패치가 적용되었습니다.",
        "patch": patch,
    }


def _apply_patch_value(
    *,
    element: Dict[str, Any],
    target_path: str,
    value: Any,
    op: str,
    strict_path: bool,
) -> bool:
    """op별로 값을 적용한다. 예: _apply_patch_value(element, "settings.title", "텍스트", "set_text", True)"""

    # 한글: 기본 텍스트/HTML/이미지 경로는 그대로 세팅한다.
    if op in {"set_text", "set_html", "set_image"}:
        return set_nested_value(element, target_path, value, strict=strict_path)

    # 한글: 강조 텍스트는 리스트 구조를 유지해야 한다.
    if op == "set_highlighted_text":
        return _set_highlighted_text(element, value, strict_path)

    # 한글: 아이콘 리스트는 배열 구조를 유지해야 한다.
    if op == "set_icon_list":
        return _set_icon_list(element, value, strict_path)

    # 한글: UiCore Counter는 number/suffix/title만 부분 업데이트한다.
    if op == "set_counter":
        return _set_counter(element, value, strict_path)

    # 한글: UiCore Icon Box는 기존 settings를 유지하며 필요한 필드만 업데이트한다.
    if op == "set_iconbox":
        return _set_icon_box(element, value, strict_path)

    # 한글: 기본 처리 (경로 그대로 세팅)
    return set_nested_value(element, target_path, value, strict=strict_path)


def _find_element(
    *,
    patched_data: Dict[str, Any],
    element_id: Optional[str],
    css_id: Optional[str],
) -> Tuple[Optional[List[Dict[str, Any]]], Optional[int], Optional[Dict[str, Any]]]:
    """중첩 포함 요소를 찾는다. 예: _find_element(patched_data=data, element_id="hero", css_id=None)"""

    elements_root = _get_elements_root(patched_data)
    for parent, index, element in _walk_elements_with_parent(elements_root):
        if element_id and element.get("id") == element_id:
            return parent, index, element
        if css_id and _matches_css_id(element.get("settings"), css_id):
            return parent, index, element

    return None, None, None


def _get_elements_root(patched_data: Any) -> List[Dict[str, Any]]:
    """Elementor 루트 elements를 반환한다. 예: _get_elements_root(patched_data)"""

    if isinstance(patched_data, list):
        return [item for item in patched_data if isinstance(item, dict)]

    if isinstance(patched_data, dict):
        elements = patched_data.get("elements")
        if isinstance(elements, list):
            return [item for item in elements if isinstance(item, dict)]

    return []


def _walk_elements_with_parent(
    elements: List[Dict[str, Any]],
) -> Iterable[Tuple[List[Dict[str, Any]], int, Dict[str, Any]]]:
    """요소와 부모 리스트를 함께 순회한다. 예: _walk_elements_with_parent(elements)"""

    for index, element in enumerate(elements):
        if not isinstance(element, dict):
            continue
        yield elements, index, element

        children = element.get("elements", [])
        if isinstance(children, list):
            yield from _walk_elements_with_parent(children)


def _matches_css_id(settings: Any, css_id: str) -> bool:
    """settings의 CSS ID가 일치하는지 확인한다. 예: _matches_css_id(settings, "hero_title")"""

    if not isinstance(settings, dict):
        return False

    # 한글: Elementor는 _element_id로 저장하는 경우가 많다.
    for key in ("_element_id", "_css_id", "css_id", "cssId", "cssid"):
        value = settings.get(key)
        if isinstance(value, str) and value.strip() == css_id:
            return True

    return False


def _remove_element_by_index(
    elements_parent: Optional[List[Dict[str, Any]]],
    element_index: Optional[int],
) -> None:
    """요소를 안전하게 제거한다. 예: _remove_element_by_index(elements, 3)"""

    if elements_parent is None or element_index is None:
        return

    if 0 <= element_index < len(elements_parent):
        elements_parent.pop(element_index)


def _set_highlighted_text(element: Dict[str, Any], value: Any, strict_path: bool) -> bool:
    """강조 텍스트 위젯에 안전하게 값 적용. 예: _set_highlighted_text(el, "문장", True)"""

    settings = element.get("settings")
    if not isinstance(settings, dict):
        return False

    content = settings.get("content")
    if not isinstance(content, list) or not content:
        # 한글: 구조가 다르면 기본 경로에 바로 세팅 시도
        return set_nested_value(element, "settings.content", value, strict=strict_path)

    # 한글: 문자열이면 첫 번째 텍스트만 교체한다.
    if isinstance(value, str):
        if isinstance(content[0], dict):
            content[0]["text"] = value
            return True
        return False

    # 한글: 리스트면 순서대로 채운다.
    if isinstance(value, list):
        for idx, text in enumerate(value):
            if idx >= len(content):
                break
            if isinstance(content[idx], dict):
                content[idx]["text"] = text
        return True

    return False


def _set_icon_list(element: Dict[str, Any], value: Any, strict_path: bool) -> bool:
    """아이콘 리스트 위젯에 안전하게 값 적용. 예: _set_icon_list(el, ["a","b"], True)"""

    settings = element.get("settings")
    if not isinstance(settings, dict):
        return False

    icon_list = settings.get("icon_list")
    if not isinstance(icon_list, list) or not icon_list:
        return set_nested_value(element, "settings.icon_list", value, strict=strict_path)

    if isinstance(value, str):
        if isinstance(icon_list[0], dict):
            icon_list[0]["text"] = value
            return True
        return False

    if isinstance(value, list):
        for idx, text in enumerate(value):
            if idx >= len(icon_list):
                break
            if isinstance(icon_list[idx], dict):
                icon_list[idx]["text"] = text
        return True

    return False


def _set_counter(element: Dict[str, Any], value: Any, strict_path: bool) -> bool:
    """카운터 위젯에 안전하게 값 적용. 예: _set_counter(el, {"number":"10","suffix":"%","title":"만족도"}, True)"""

    settings = element.get("settings")
    if not isinstance(settings, dict):
        return False

    if isinstance(value, dict):
        # 한글: 기존 설정을 보존하며 필요한 필드만 갱신
        for key in ("number", "suffix", "title"):
            if key in value:
                settings[key] = value[key]
        return True

    # 한글: 문자열이면 number로만 처리
    if isinstance(value, str):
        settings["number"] = value
        return True

    return False


def _set_icon_box(element: Dict[str, Any], value: Any, strict_path: bool) -> bool:
    """아이콘 박스 위젯에 안전하게 값 적용. 예: _set_icon_box(el, {...}, True)"""

    settings = element.get("settings")
    if not isinstance(settings, dict):
        return False

    if not isinstance(value, dict):
        # 한글: 비정상 값은 그대로 세팅 시도
        return set_nested_value(element, "settings", value, strict=strict_path)

    # 한글: 텍스트 계열
    for key in ("title", "subtitle", "description"):
        if key in value:
            settings[key] = value[key]

    # 한글: 링크/버튼 텍스트가 있는 경우
    if "button_text" in value:
        settings["button_text"] = value["button_text"]
    if "button_url" in value:
        settings["button_url"] = value["button_url"]

    # 한글: 아이콘은 문자열 URL 또는 객체 형태를 지원
    if "icon" in value:
        settings["icon"] = value["icon"]
    if "image" in value:
        settings["image"] = value["image"]

    return True
