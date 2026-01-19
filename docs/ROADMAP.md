# 구현 로드맵 (project.md ↔ 코드 매핑)

## STEP 1. 인프라 + 워드프레스 자동 설치
- 상태: 미구현
- 예정 위치: `src/site_factory/wordpress/` 또는 `scripts/vps/`

## STEP 2. 템플릿 주입(Kit/Export Import)
- 상태: 미구현
- 예정 위치: `src/site_factory/wordpress/`

## STEP 3. site_spec.json 생성
- 상태: 스캐폴딩
- 현재 위치: `data/mock/site_spec.sample.json`
- 예정 확장: LLM 연동 모듈

## STEP 4. 이미지 생성/업로드
- 상태: 미구현
- 예정 위치: `src/site_factory/media/`

## STEP 5. template_adapter.json 기반 Elementor 주입
- 상태: 스캐폴딩
- 현재 위치: `src/site_factory/patcher.py`, `data/mock/template_adapter.sample.json`

## STEP 6. RankMath SEO 주입
- 상태: 미구현
- 예정 위치: `src/site_factory/seo/`

## STEP 7. URL 치환 + 캐시 플러시
- 상태: 미구현
- 예정 위치: `src/site_factory/wordpress/`

## STEP 8. Smoke Test
- 상태: 미구현
- 예정 위치: `src/site_factory/smoke/`
