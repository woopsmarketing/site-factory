<!-- v1.0 - vps 스크립트 규칙 생성 (2026-01-20) -->
<!-- 요약: VPS 부트스트랩/프로비저닝 스크립트 개발 규칙 정리. 예: 옵션 추가/변경 시 본 문서 참고 -->
# Module Context
- `scripts/vps`는 서버 초기화와 WordPress 사이트 프로비저닝 스크립트를 담당한다.
- `bootstrap.sh`는 Ubuntu 22.04 기준 필수 패키지와 WP-CLI 설치를 수행한다.
- `provision_site.sh`는 도메인/DB/NGINX/WP 설치를 자동화한다.

# Tech Stack & Constraints
- Bash 기반이며 Ubuntu 22.04 환경을 전제로 한다.
- `apt-get`, `nginx`, `php-fpm`, `mariadb`, `wp-cli` 의존성이 필요하다.
- 루트 권한이 필요하므로 `require_root` 체크를 유지한다.
- 사용자 오류는 `print_error`로 친절한 메시지를 출력하고 즉시 종료한다.

# Implementation Patterns
- 스크립트 시작 시 `set -euo pipefail`을 유지한다.
- 공통 메시지 출력은 `print_info` / `print_error` 유틸을 사용한다.
- 필수 명령어는 `require_command`로 사전 검증한다.
- DB 식별자는 `sanitize_identifier`로 정규화해 안전하게 만든다.
- Nginx 설정은 `/etc/nginx/sites-available`에 작성 후 `nginx -t`로 검증하고 리로드한다.
- 사이트 루트는 `/var/www/wp-sites/{domain}` 구조를 유지한다.

# Testing Strategy
- Ubuntu 22.04 테스트 서버에서 아래 명령으로 수동 검증한다.
```
sudo bash scripts/vps/bootstrap.sh
sudo bash scripts/vps/provision_site.sh --domain t1.example.com --admin-email admin@example.com --admin-pass "StrongPass123!"
```
- `nginx -t` 통과 및 `systemctl status nginx` 확인을 기본 점검으로 한다.

# Local Golden Rules
- 모든 코드에 한글 주석을 포함한다.
- 에러 가능성이 있는 영역은 사전 체크로 실패 지점을 명확히 분리한다.
- 옵션 추가 시 `usage()` 출력과 기본값 규칙을 함께 갱신한다.
- 신규 패키지 의존성은 `bootstrap.sh` 설치 목록에 반영한다.
