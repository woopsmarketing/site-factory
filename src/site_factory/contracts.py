# v0.1 - 계약(스키마) 검증 추가 (2026-01-16)
# 기능: site_spec / adapter 필수 키 검증 (예: validate_site_spec(site_spec))

from typing import Any, Dict, List

from .utils.dict_utils import has_nested_value
from .utils.error_utils import FriendlyError


REQUIRED_SITE_SPEC_KEYS: List[str] = [
    "brand.name",
    "brand.tagline",
    "brand.contact.email",
    "design.colors.primary",
    "design.colors.secondary",
    "design.colors.accent",
    "design.fonts.heading",
    "design.fonts.body",
    "pages.home.hero.h1",
    "pages.home.hero.sub",
    "pages.home.hero.cta_text",
    "pages.home.hero.cta_url",
    "seo.home.title",
    "seo.home.description",
    "seo.organization.name",
    "seo.organization.url",
]


def validate_site_spec(site_spec: Dict[str, Any]) -> Dict[str, Any]:
    """site_spec 필수 키를 검증한다. 예: validate_site_spec(site_spec)"""

    missing_keys = [
        key for key in REQUIRED_SITE_SPEC_KEYS if not has_nested_value(site_spec, key)
    ]

    if missing_keys:
        missing_text = ", ".join(missing_keys)
        raise FriendlyError(
            user_message=f"site_spec 필수 키가 누락되었습니다: {missing_text}"
        )

    return {
        "status": "ok",
        "missing_keys": [],
        "checked_keys": len(REQUIRED_SITE_SPEC_KEYS),
    }


def validate_adapter(adapter: Dict[str, Any]) -> Dict[str, Any]:
    """template_adapter 기본 구조를 검증한다. 예: validate_adapter(adapter)"""

    error_messages: List[str] = []

    if not isinstance(adapter.get("template_id"), str):
        error_messages.append("adapter.template_id가 필요합니다.")

    pages = adapter.get("pages")
    if not isinstance(pages, list) or not pages:
        error_messages.append("adapter.pages는 비어있지 않은 리스트여야 합니다.")

    if isinstance(pages, list):
        for page_index, page in enumerate(pages):
            patches = page.get("patches")
            if not isinstance(patches, list):
                error_messages.append(f"pages[{page_index}].patches는 리스트여야 합니다.")
                continue

            for patch_index, patch in enumerate(patches):
                for field_name in ("key", "element_id", "path", "op"):
                    if field_name not in patch:
                        error_messages.append(
                            f"patches[{patch_index}]에 '{field_name}'가 필요합니다."
                        )

    if error_messages:
        raise FriendlyError(user_message="; ".join(error_messages))

    return {
        "status": "ok",
        "page_count": len(pages) if isinstance(pages, list) else 0,
    }
