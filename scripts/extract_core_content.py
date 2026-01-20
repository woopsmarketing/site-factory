#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
핵심 콘텐츠만 추출 (Hero, CTA, Feature)
- 실제 사용자가 보는 텍스트만
- 이미지 위젯만
- 버튼/제목/본문만

사용 예시:
    python scripts/extract_core_content.py output/filtered_manifest.json output/core_content.json
"""

import json
import sys
import re
from pathlib import Path


# 제외할 기본값 패턴
EXCLUDE_PATTERNS = [
    r'^This is Tooltip$',
    r'^my-header$',
    r'left,right',
    r'square\|circle',
    r'🎃\|🎄\|💜',
    r'^M\d+',  # SVG path
    r'^(center|left|right|top|bottom)$',
    r'^(yes|no)$',
    r'^(full|contain|cover|auto)$',
    r'^(fadeIn|fadeOut|zoom|slide)',  # 애니메이션
    r'^(fast|slow|normal)$',
    r'^(custom|default|classic)$',
    r'^(solid|dashed|dotted)$',
    r'^(row|column)$',
    r'^(space-between|center|flex-)',
    r'^(grow|none|initial|inherit)$',
    r'^(uppercase|lowercase)$',
]

# 핵심 위젯 타입만
CORE_WIDGETS = [
    'heading',
    'text-editor',
    'button',
    'highlighted-text',
    'icon-list',
    'image',
]


def is_exclude(text: str) -> bool:
    """제외할 텍스트인지 판단"""
    for pattern in EXCLUDE_PATTERNS:
        if re.match(pattern, text, re.IGNORECASE):
            return True
    return False


def is_meaningful_content(candidate: dict) -> bool:
    """의미 있는 콘텐츠인지 판단"""
    
    # 위젯 타입 확인
    widget_type = candidate.get('widget_type')
    if widget_type and widget_type not in CORE_WIDGETS:
        return False
    
    # 이미지는 무조건 포함
    if candidate.get('field_type') == 'image':
        return True
    
    # 텍스트 확인
    preview = candidate.get('preview', '')
    
    # 빈 값 제외
    if not preview or len(preview) < 2:
        return False
    
    # 기본값 제외
    if is_exclude(preview):
        return False
    
    # 한글이 포함되어 있으면 OK
    if re.search(r'[가-힣]', preview):
        return True
    
    # 영문 단어가 2개 이상이면 OK (예: "Get Started")
    if len(preview.split()) >= 2 and re.search(r'[a-zA-Z]', preview):
        return True
    
    return False


def extract_core(manifest_path: str, output_path: str):
    """핵심 콘텐츠만 추출"""
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    core = []
    stats = {
        'heading': 0,
        'text_editor': 0,
        'button': 0,
        'highlighted_text': 0,
        'icon_list': 0,
        'image': 0,
        'other': 0,
    }
    
    for candidate in data['candidates']:
        if is_meaningful_content(candidate):
            core.append(candidate)
            
            # 통계
            widget_type = candidate.get('widget_type', 'other')
            key = widget_type.replace('-', '_')
            if key in stats:
                stats[key] += 1
            else:
                stats['other'] += 1
    
    # 결과 저장
    result = {
        **data,
        'candidates': core,
        'core_stats': {
            'total_count': len(core),
            **stats
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 핵심 콘텐츠 추출 완료:")
    print(f"   필터 전: {len(data['candidates'])}개")
    print(f"   핵심만: {len(core)}개")
    print(f"   - Heading: {stats['heading']}개")
    print(f"   - Text Editor: {stats['text_editor']}개")
    print(f"   - Button: {stats['button']}개")
    print(f"   - Highlighted Text: {stats['highlighted_text']}개")
    print(f"   - Icon List: {stats['icon_list']}개")
    print(f"   - Image: {stats['image']}개")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("사용법: python scripts/extract_core_content.py <입력> <출력>")
        sys.exit(1)
    
    extract_core(sys.argv[1], sys.argv[2])
