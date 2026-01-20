#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
섹션 단위 스캐너
- Elementor 페이지를 섹션별로 분석
- 각 섹션 내 주입 가능한 위젯 추출
- 대화형 인터페이스로 선택 지원

사용 예시:
    python -m site_factory.cli section-scan \
      --input data/elementor-home.json \
      --output sections/t1_home.json
"""

from typing import Dict, List, Any
import json
from pathlib import Path


class SectionScanner:
    """섹션 단위로 Elementor 구조 분석"""
    
    # 주입 가능한 위젯 타입
    INJECTABLE_WIDGETS = {
        'heading': '제목',
        'text-editor': '본문',
        'button': '버튼',
        'image': '이미지',
        'icon': '아이콘',
        'icon-list': '아이콘 리스트',
        'highlighted-text': '강조 텍스트',
    }
    
    def __init__(self, elementor_data: List[Dict]):
        self.elementor_data = elementor_data
        self.sections = []
    
    def scan(self) -> List[Dict]:
        """섹션별로 구조 추출"""
        section_index = 0
        
        for element in self.elementor_data:
            if element.get('elType') == 'section':
                section = self._extract_section(element, section_index)
                if section['widgets']:  # 위젯이 있는 섹션만
                    self.sections.append(section)
                    section_index += 1
        
        return self.sections
    
    def _extract_section(self, section_element: Dict, index: int) -> Dict:
        """섹션 정보 추출"""
        
        # 섹션 기본 정보
        section_info = {
            'index': index,
            'element_id': section_element.get('id'),
            'name': f'section_{index}',  # 기본 이름
            'suggested_name': self._suggest_section_name(section_element, index),
            'widgets': []
        }
        
        # 섹션 내 모든 위젯 추출
        widgets = self._extract_widgets(section_element)
        
        for widget_idx, widget in enumerate(widgets):
            widget_info = {
                'index': widget_idx,
                'element_id': widget.get('id'),
                'widget_type': widget.get('widgetType'),
                'widget_type_kr': self.INJECTABLE_WIDGETS.get(
                    widget.get('widgetType'), 
                    widget.get('widgetType')
                ),
                'preview': self._get_widget_preview(widget),
                'path': self._get_widget_path(widget),
                'injectable': widget.get('widgetType') in self.INJECTABLE_WIDGETS
            }
            
            section_info['widgets'].append(widget_info)
        
        return section_info
    
    def _suggest_section_name(self, section_element: Dict, index: int) -> str:
        """섹션 이름 자동 추천"""
        
        # 첫 번째 섹션은 보통 Hero
        if index == 0:
            return 'hero'
        
        # 위젯 내용으로 추측
        widgets = self._extract_widgets(section_element)
        
        # 가격 관련 키워드
        for widget in widgets:
            preview = self._get_widget_preview(widget).lower()
            if any(kw in preview for kw in ['price', '가격', 'plan', '요금']):
                return 'pricing'
            if any(kw in preview for kw in ['feature', '기능', '특징']):
                return 'features'
            if any(kw in preview for kw in ['about', '소개', '회사']):
                return 'about'
            if any(kw in preview for kw in ['contact', '연락', '문의']):
                return 'contact'
        
        return f'section_{index}'
    
    def _extract_widgets(self, element: Dict) -> List[Dict]:
        """재귀적으로 모든 위젯 추출"""
        widgets = []
        
        if element.get('widgetType'):
            widgets.append(element)
        
        # 자식 요소 탐색 (컬럼, 컨테이너 등)
        for child in element.get('elements', []):
            widgets.extend(self._extract_widgets(child))
        
        return widgets
    
    def _get_widget_preview(self, widget: Dict) -> str:
        """위젯 미리보기 텍스트"""
        widget_type = widget.get('widgetType')
        settings = widget.get('settings', {})
        
        # 타입별 미리보기
        if widget_type == 'heading':
            return settings.get('title', '(제목 없음)')
        
        elif widget_type == 'text-editor':
            editor = settings.get('editor', '')
            # HTML 태그 제거하고 첫 50자만
            import re
            text = re.sub('<[^<]+?>', '', editor)
            return text[:50] + ('...' if len(text) > 50 else '')
        
        elif widget_type == 'button':
            return settings.get('text', '(버튼 텍스트 없음)')
        
        elif widget_type == 'image':
            url = settings.get('image', {}).get('url', '')
            filename = url.split('/')[-1] if url else '(이미지 없음)'
            return filename
        
        elif widget_type == 'highlighted-text':
            content = settings.get('content', [])
            if content:
                return ' '.join([c.get('text', '') for c in content])
            return '(강조 텍스트 없음)'
        
        return f'({widget_type})'
    
    def _get_widget_path(self, widget: Dict) -> str:
        """위젯 값을 주입할 경로"""
        widget_type = widget.get('widgetType')
        
        # 타입별 기본 경로
        paths = {
            'heading': 'settings.title',
            'text-editor': 'settings.editor',
            'button': 'settings.text',
            'image': 'settings.image.url',
            'highlighted-text': 'settings.content',
        }
        
        return paths.get(widget_type, 'settings')


def print_sections_interactive(sections: List[Dict]) -> Dict:
    """
    대화형으로 섹션 구조 출력 및 선택
    
    Returns:
        선택된 주입 포인트 정보
    """
    print("\n" + "="*60)
    print("📄 페이지 구조 분석 결과")
    print("="*60 + "\n")
    
    selected_injections = []
    
    for section in sections:
        print(f"\n{'─'*60}")
        print(f"🔷 섹션 {section['index']}: {section['suggested_name']}")
        print(f"{'─'*60}\n")
        
        # 주입 가능한 위젯만 표시
        injectable = [w for w in section['widgets'] if w['injectable']]
        
        if not injectable:
            print("  ℹ️  주입 가능한 위젯이 없습니다.\n")
            continue
        
        for widget in injectable:
            print(f"  [{widget['index']}] {widget['widget_type_kr']:12} │ {widget['preview']}")
        
        print(f"\n  💡 주입할 위젯 번호를 입력하세요 (쉼표로 구분, 예: 0,1,3)")
        print(f"     또는 Enter로 건너뛰기")
        
        selection = input(f"\n  선택 ({section['suggested_name']}): ").strip()
        
        if selection:
            indices = [int(i.strip()) for i in selection.split(',')]
            for idx in indices:
                widget = injectable[idx]
                selected_injections.append({
                    'section': section['suggested_name'],
                    'section_index': section['index'],
                    'widget_index': idx,
                    'element_id': widget['element_id'],
                    'widget_type': widget['widget_type'],
                    'path': widget['path'],
                    'preview': widget['preview']
                })
    
    print("\n" + "="*60)
    print(f"✅ 총 {len(selected_injections)}개 주입 포인트 선택됨")
    print("="*60 + "\n")
    
    return {
        'sections': sections,
        'selected_injections': selected_injections
    }


def generate_adapter_from_selection(
    selection_data: Dict,
    template_id: str,
    page_slug: str
) -> Dict:
    """선택 결과로 어댑터 생성"""
    
    patches = []
    
    for injection in selection_data['selected_injections']:
        # site_spec 키 자동 생성
        section = injection['section']
        widget_type = injection['widget_type']
        index = injection['widget_index']
        
        key = f"{section}.{widget_type}_{index}"
        
        patch = {
            'key': key,
            'element_id': injection['element_id'],
            'path': injection['path'],
            'op': 'set_text' if widget_type != 'image' else 'set_image',
            'comment': injection['preview']
        }
        
        patches.append(patch)
    
    return {
        'template_id': template_id,
        'pages': [
            {
                'post_slug': page_slug,
                'patches': patches
            }
        ]
    }
