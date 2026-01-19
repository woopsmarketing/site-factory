# Elementor 스캐너 가이드

## 목적
- Elementor JSON이 너무 길어도 **주입 후보만 추출**해서 빠르게 매핑할 수 있도록 한다.
- 결과물은 `manifest.json`과 `adapter_skeleton.json`으로 저장된다.

## 사용법
```
python -m site_factory.cli scan --input data/mock/elementor.sample.json --output-dir output --page-slug home --template-id t1
```

### 출력 파일
- `output/manifest.json`: 후보 목록과 요약 정보
- `output/adapter_skeleton.json`: patch 리스트 초안

## 추천 규칙 (강제하면 자동화가 쉬워짐)
- Elementor 위젯의 **Advanced → CSS ID**를 고정 규칙으로 설정
  - 예: `hero_title`, `hero_subtitle`, `hero_cta`, `footer_contact`
- 텍스트/링크/이미지의 주입 포인트를 **최소 10~20개만 먼저 고정**
- 나머지는 스캐너 후보에서 선택해서 확장

## 주의사항
- 스캐너는 “후보 추출”까지만 수행한다.
- 실제 매핑은 `adapter_skeleton.json`의 `key`를 `site_spec` 경로로 교체해야 한다.
- 필요하면 patch에 `css_id`를 추가해 CSS ID 기준으로도 매칭할 수 있다.
