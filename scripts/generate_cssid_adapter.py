#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSS ID 기반 어댑터 자동 생성

사용:
    python scripts/generate_cssid_adapter.py \
      data/elementor-home-cssid.json \
      data/adapters/t1_home_cssid.json \
      --template-id t1 \
      --page-slug home
"""

import json
import sys
import argparse


def extract_css_ids(elementor_data, parent_path=""):
    """CSS ID가 있는 위젯 추출"""
    css_id_map = []
    
    for element in elementor_data:
        element_id = element.get('id')
        widget_type = element.get('widgetType') or element.get('elType')
        settings = element.get('settings', {})
        css_id = settings.get('_element_id')
        
        if css_id:
            # 위젯 타입별 기본 경로
            path_map = {
                'heading': 'settings.title',
                'text-editor': 'settings.editor',
                'button': 'settings.text',
                'image': 'settings.image.url',
                'icon-list': 'settings.icon_list',
                'highlighted-text': 'settings.content',
                'uicore-counter': 'settings',  # Counter는 복합 필드
                'uicore-icon-box': 'settings',  # Icon Box도 복합 필드
            }
            
            op_map = {
                'heading': 'set_text',
                'text-editor': 'set_html',
                'button': 'set_text',
                'image': 'set_image',
                'icon-list': 'set_text',
                'highlighted-text': 'set_text',
                'uicore-counter': 'set_counter',
                'uicore-icon-box': 'set_iconbox',
            }
            
            css_id_map.append({
                'css_id': css_id,
                'element_id': element_id,
                'widget_type': widget_type,
                'path': path_map.get(widget_type, 'settings'),
                'op': op_map.get(widget_type, 'set_text')
            })
        
        # 자식 요소 재귀
        if 'elements' in element:
            css_id_map.extend(extract_css_ids(element['elements'], parent_path))
    
    return css_id_map


def generate_adapter(elementor_json_path, output_path, template_id, page_slug):
    """CSS ID 기반 어댑터 생성"""
    
    with open(elementor_json_path, 'r', encoding='utf-8') as f:
        elementor_data = json.load(f)
    
    css_id_map = extract_css_ids(elementor_data)
    
    patches = []
    for item in css_id_map:
        patch = {
            'key': item['css_id'],
            'element_id': item['element_id'],
            'path': item['path'],
            'op': item['op'],
            'widget_type': item['widget_type']
        }
        patches.append(patch)
    
    adapter = {
        'template_id': template_id,
        'pages': [
            {
                'post_slug': page_slug,
                'patches': patches
            }
        ]
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(adapter, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 어댑터 생성 완료: {output_path}")
    print(f"   총 {len(patches)}개 CSS ID 발견")
    print(f"\n📋 CSS ID 목록:")
    for item in css_id_map:
        print(f"   - {item['css_id']:25} ({item['widget_type']})")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CSS ID 기반 어댑터 생성')
    parser.add_argument('input', help='Elementor JSON 파일')
    parser.add_argument('output', help='출력 어댑터 파일')
    parser.add_argument('--template-id', required=True, help='템플릿 ID')
    parser.add_argument('--page-slug', required=True, help='페이지 슬러그')
    
    args = parser.parse_args()
    
    generate_adapter(args.input, args.output, args.template_id, args.page_slug)
