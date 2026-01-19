# v0.2 - 중첩 요소/ CSS ID 대응 추가 (2026-01-19)
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

    success = set_nested_value(element, target_path, value, strict=strict_path)
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

    for key in ("_css_id", "css_id", "cssId", "cssid"):
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
