#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manifest 필터링 스크립트
- 의미 있는 콘텐츠 후보만 추출
- CSS ID가 있는 항목 우선
- 짧은 텍스트(ID, 숫자)는 제외

사용 예시:
    python scripts/filter_manifest.py output/manifest.json output/filtered_manifest.json
"""

import json
import sys
from pathlib import Path


def is_meaningful_text(preview: str) -> bool:
    """의미 있는 텍스트인지 판단"""
    if not preview or len(preview) < 3:
        return False
    
    # 숫자만 있으면 제외
    if preview.isdigit():
        return False
    
    # UUID 형식 제외 (예: 32bd91f)
    if len(preview) == 7 and all(c in '0123456789abcdef' for c in preview):
        return False
    
    # 색상 코드 제외
    if preview.startswith('#') or ',' in preview and all(c in '#0123456789ABCDEF, ' for c in preview):
        return False
    
    # transition, easing 등 CSS 속성 제외
    css_keywords = ['linear', 'ease', 'all', 'box', 'border', 'px', 'em', 'rem']
    if any(kw in preview.lower() for kw in css_keywords):
        return False
    
    return True


def filter_candidates(manifest_path: str, output_path: str):
    """의미 있는 후보만 필터링"""
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    filtered = []
    stats = {
        'has_css_id': 0,
        'meaningful_text': 0,
        'images': 0,
        'links': 0
    }
    
    for candidate in data['candidates']:
        # CSS ID가 있으면 무조건 포함
        if candidate.get('css_id'):
            filtered.append(candidate)
            stats['has_css_id'] += 1
            continue
        
        # 이미지는 포함
        if candidate.get('field_type') == 'image':
            filtered.append(candidate)
            stats['images'] += 1
            continue
        
        # 링크는 포함
        if candidate.get('field_type') == 'link':
            filtered.append(candidate)
            stats['links'] += 1
            continue
        
        # 텍스트는 의미 있는 것만
        if candidate.get('field_type') == 'text':
            preview = candidate.get('preview', '')
            if is_meaningful_text(preview):
                filtered.append(candidate)
                stats['meaningful_text'] += 1
    
    # 결과 저장
    result = {
        **data,
        'candidates': filtered,
        'filter_stats': {
            'original_count': len(data['candidates']),
            'filtered_count': len(filtered),
            **stats
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 필터링 완료:")
    print(f"   원본: {result['filter_stats']['original_count']}개")
    print(f"   필터: {result['filter_stats']['filtered_count']}개")
    print(f"   - CSS ID: {stats['has_css_id']}개")
    print(f"   - 텍스트: {stats['meaningful_text']}개")
    print(f"   - 이미지: {stats['images']}개")
    print(f"   - 링크: {stats['links']}개")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("사용법: python scripts/filter_manifest.py <입력> <출력>")
        sys.exit(1)
    
    filter_candidates(sys.argv[1], sys.argv[2])
