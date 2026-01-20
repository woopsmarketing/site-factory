#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
자동 매칭 시스템
- Widget Type별로 자동으로 콘텐츠 매칭
- 어댑터 수동 작성 불필요

사용 예시:
    from site_factory.auto_matcher import AutoMatcher
    
    matcher = AutoMatcher(elementor_json, site_spec)
    patches = matcher.generate_patches()
"""

from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class AutoMatcher:
    """Widget Type별 자동 매칭"""
    
    # Widget Type → site_spec 경로 매핑
    WIDGET_MAPPING = {
        'heading': {
            'site_spec_array': 'content.titles',
            'target_path': 'settings.title',
            'op': 'set_text'
        },
        'text-editor': {
            'site_spec_array': 'content.paragraphs',
            'target_path': 'settings.editor',
            'op': 'set_html'
        },
        'button': {
            'site_spec_array': 'content.ctas',
            'target_path': 'settings.text',
            'op': 'set_text'
        },
        'highlighted-text': {
            'site_spec_array': 'content.highlights',
            'target_path': 'settings.content',  # 특수 처리 필요
            'op': 'set_text'
        },
        'image': {
            'site_spec_array': 'images.list',
            'target_path': 'settings.image.url',
            'op': 'set_image'
        },
    }
    
    def __init__(self, elementor_data: List[Dict], site_spec: Dict):
        """
        Args:
            elementor_data: Elementor JSON (파싱된 요소 리스트)
            site_spec: 사이트 스펙
        """
        self.elementor_data = elementor_data
        self.site_spec = site_spec
        self.counters = {}  # widget_type별 카운터
    
    def generate_patches(self) -> List[Dict]:
        """자동으로 패치 생성"""
        patches = []
        
        for element in self._traverse_elements(self.elementor_data):
            widget_type = element.get('widgetType')
            element_id = element.get('id')
            
            if not widget_type or not element_id:
                continue
            
            # 매핑 규칙 확인
            mapping = self.WIDGET_MAPPING.get(widget_type)
            if not mapping:
                continue
            
            # 카운터 증가
            if widget_type not in self.counters:
                self.counters[widget_type] = 0
            else:
                self.counters[widget_type] += 1
            
            index = self.counters[widget_type]
            
            # site_spec 경로 생성
            site_spec_key = f"{mapping['site_spec_array']}[{index}]"
            
            # 패치 생성
            patch = {
                'key': site_spec_key,
                'element_id': element_id,
                'path': mapping['target_path'],
                'op': mapping['op'],
                'auto_matched': True,
                'widget_type': widget_type,
                'index': index
            }
            
            patches.append(patch)
            logger.debug(f"자동 매칭: {widget_type}[{index}] → {element_id}")
        
        logger.info(f"총 {len(patches)}개 패치 자동 생성")
        logger.info(f"통계: {self.counters}")
        
        return patches
    
    def _traverse_elements(self, elements: List[Dict]) -> List[Dict]:
        """
        Elementor JSON을 순회하며 모든 위젯 추출
        
        중첩된 구조(컨테이너, 섹션 등)도 재귀적으로 탐색
        """
        for element in elements:
            yield element
            
            # 자식 요소가 있으면 재귀
            if 'elements' in element:
                yield from self._traverse_elements(element['elements'])


def generate_auto_adapter(
    elementor_json: List[Dict],
    site_spec: Dict,
    page_slug: str,
    template_id: str
) -> Dict:
    """
    자동으로 어댑터 생성
    
    Args:
        elementor_json: Elementor JSON 데이터
        site_spec: 사이트 스펙
        page_slug: 페이지 슬러그
        template_id: 템플릿 ID
    
    Returns:
        어댑터 JSON
    """
    matcher = AutoMatcher(elementor_json, site_spec)
    patches = matcher.generate_patches()
    
    return {
        'template_id': template_id,
        'auto_generated': True,
        'pages': [
            {
                'post_slug': page_slug,
                'patches': patches
            }
        ]
    }
