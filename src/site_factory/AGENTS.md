<!-- v1.1 - site_factory 모듈 규칙 정비 (2026-01-20) -->
<!-- 요약: 파이프라인/스캐너/패처 개발 규칙과 테스트 지침을 정리. 예: 신규 패치 op 추가 시 참조 -->
# Module Context
- `site_factory`는 WordPress Site Factory의 CLI/파이프라인/스캐너/패처 로직을 담당한다.
- 입력은 `site_spec.json`, `template_adapter.json`, Elementor JSON이며 계약 검증 후 처리한다.
- 주요 산출물은 `patched_elementor.json`, `patch_results.json`, `run_report.json`이다.

# Tech Stack & Constraints
- Python 3.10+ 표준 라이브러리 기반으로 동작한다.
- 입출력은 JSON 파일이며 `pathlib.Path`를 사용한다.
- `.env`는 사용하지 않는다. 설정은 JSON 파일로만 다룬다.
- 사용자 에러는 `FriendlyError`로 감싸고 상세는 `detail`에만 담는다.
- CLI 엔트리 포인트는 `python -m site_factory.cli`를 유지한다.

# Implementation Patterns
- 파일 상단에 버전/기능 요약 주석과 간단한 사용 예시를 유지한다.
- 함수 docstring에 간단한 예시(`예: ...`)를 포함한다.
- I/O는 `utils.io_utils`를 사용하고 중첩 경로 처리는 `utils.dict_utils`로 통일한다.
- 파이프라인 의존성은 `PipelineDependencies`로 주입 가능하게 유지한다.
- 로깅은 `utils.log_utils.create_logger`를 사용한다.
- 반복되는 로직은 유틸 함수로 분리하고 함수는 작게 유지한다.
- 결과물은 `output/` 아래 JSON으로 저장한다.

# Testing Strategy
- Mock 파이프라인 실행
```
python -m site_factory.cli run --use-mock --config config.sample.json --output-dir output
```
- 스캐너 실행
```
python -m site_factory.cli scan --input data/mock/elementor.sample.json --output-dir output --page-slug home --template-id t1
```
- 권장 유닛 테스트
  - `dict_utils` 중첩 경로 처리
  - `patcher`의 패치 적용/삭제 동작
  - `scanner`의 후보 추출 규칙
  - `contracts`의 스키마 검증 규칙

# Local Golden Rules
- 모든 코드에 한글 주석을 포함한다.
- 에러 가능성이 있는 영역은 사전 체크 또는 `try/except`로 예외를 명확히 처리한다.
- 테스트 가능성을 위해 의존성 주입 구조를 유지한다.
- 새 CLI/유틸을 추가할 때는 실행 가능한 엔트리 포인트를 제공한다.
- 계약 변경 시 `contracts.py`와 mock 샘플, 문서를 함께 갱신한다.
