<!-- v1.1 - AGENTS 규칙 체계 정비 (2026-01-20) -->
<!-- 요약: WordPress Site Factory 스캐폴딩의 실행/규칙/라우팅을 정리. 예: 신규 규칙 추가 시 본 문서 갱신 -->
# Project Context & Operations
- 이 프로젝트는 WordPress Site Factory를 위한 파이프라인/스캐너 스캐폴딩이다.
- 핵심 흐름은 `site_spec`, `template_adapter`, Elementor JSON을 검증하고 패치 결과를 산출한다.
- 주요 산출물은 `patched_elementor.json`, `patch_results.json`, `run_report.json`이다.
- Tech Stack: Python 3.10+ (CLI), Bash (Ubuntu 22.04), WP-CLI, JSON 기반 입출력.
- `.env`는 사용하지 않으며 설정은 `config.local.json` 등으로 분리한다.

## Operational Commands
- 로컬(Windows) 기본 설정
```
python -m venv venv
.\venv\Scripts\activate
set PYTHONPATH=src
```
- Mock 파이프라인 실행
```
python -m site_factory.cli run --use-mock --config config.sample.json --output-dir output
```
- Elementor 스캐너 실행
```
python -m site_factory.cli scan --input data/mock/elementor.sample.json --output-dir output --page-slug home --template-id t1
```
- VPS 부트스트랩(Ubuntu 22.04)
```
sudo bash scripts/vps/bootstrap.sh
```
- VPS 사이트 프로비저닝
```
sudo bash scripts/vps/provision_site.sh --domain t1.example.com --admin-email admin@example.com --admin-pass "StrongPass123!"
```
- 테스트
  - 자동 테스트는 현재 없음. 위 mock/scan 실행 결과 JSON을 기본 점검으로 사용한다.

# Golden Rules
## Immutable
- `.env` 파일을 생성하거나 수정하지 않는다.
- 사용자 노출 에러는 `FriendlyError`로 감싸고 친절한 메시지를 제공한다.
- Elementor JSON을 수동 편집하지 않고 스캐너/어댑터/패처 흐름을 유지한다.
- 계약 변경 시 `validate_site_spec`, `validate_adapter`, mock 샘플을 함께 갱신한다.

## Do's & Don'ts
- Do: 입출력은 `Path`와 `io_utils`로 일관되게 처리한다.
- Do: 의존성 주입 구조(`PipelineDependencies`)를 유지해 테스트 가능성을 확보한다.
- Do: 로그는 `log_utils.create_logger`로 통일한다.
- Do: 파일 상단에 버전/기능 요약 주석과 간단한 사용 예시를 유지한다.
- Do: 예외 가능성이 있으면 사전 체크 또는 `try/except`로 친절한 메시지를 제공한다.
- Don't: site_spec 키를 코드에 하드코딩해 분기 폭증을 유도하지 않는다.
- Don't: patch op 추가/변경 시 문서와 검증 로직을 누락하지 않는다.

# Standards & References
- 코드 컨벤션: 명확한 변수/함수명, 함수 docstring에 예시 표기.
- 커밋 메시지: `feat:` `fix:` `docs:` `refactor:` `test:` `chore:` 형태로 간결하게 작성.
- 참고 문서: `README.md`, `docs/ENV_SETUP.md`, `docs/SCANNER_GUIDE.md`, `project.md`.
- Maintenance Policy: 규칙과 코드의 괴리가 발생하면 즉시 문서 업데이트를 제안한다.

# Context Map (Action-Based Routing) [CRITICAL]
- **[파이프라인/스캐너/패처 로직 수정](./src/site_factory/AGENTS.md)** — CLI, 계약 검증, JSON 패치 로직 변경 시.
- **[VPS 프로비저닝/부트스트랩 스크립트](./scripts/vps/AGENTS.md)** — 서버 설치/워드프레스 자동화 스크립트 수정 시.
