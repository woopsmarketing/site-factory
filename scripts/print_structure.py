#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Elementor 구조를 보기 좋게 출력

사용:
    python scripts/print_structure.py data/elementor-home.json
"""

import json
import sys


def print_widget(widget, indent=0):
    """위젯 정보 출력"""
    prefix = "  " * indent
    
    widget_type = widget.get('widgetType', widget.get('elType'))
    element_id = widget.get('id')
    settings = widget.get('settings', {})
    
    # 미리보기 텍스트
    preview = ""
    if widget_type == 'heading':
        preview = settings.get('title', '')
    elif widget_type == 'text-editor':
        preview = settings.get('editor', '')[:50]
    elif widget_type == 'button':
        preview = settings.get('text', '')
    elif widget_type == 'image':
        preview = settings.get('image', {}).get('url', '').split('/')[-1]
    
    # CSS ID 확인
    css_id = settings.get('_element_id', '')
    css_info = f" [CSS ID: {css_id}]" if css_id else ""
    
    print(f"{prefix}📌 {widget_type:15} │ ID: {element_id}{css_info}")
    if preview:
        print(f"{prefix}   → {preview}")


def traverse(elements, indent=0):
    """재귀적으로 구조 탐색"""
    for element in elements:
        el_type = element.get('elType')
        
        if el_type == 'section':
            print("\n" + "─" * 60)
            print(f"🔷 SECTION │ ID: {element.get('id')}")
            print("─" * 60)
        elif el_type == 'container':
            print(f"{'  ' * indent}📦 Container │ ID: {element.get('id')}")
        elif element.get('widgetType'):
            print_widget(element, indent)
        
        # 자식 요소
        children = element.get('elements', [])
        if children:
            traverse(children, indent + 1)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("사용법: python scripts/print_structure.py <elementor.json>")
        sys.exit(1)
    
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("\n" + "=" * 60)
    print("📄 ELEMENTOR 구조")
    print("=" * 60)
    
    traverse(data)
    
    print("\n" + "=" * 60)
    print("✅ 완료")
    print("=" * 60)
