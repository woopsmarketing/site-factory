#!/usr/bin/env bash
# v0.1 - 워드프레스 사이트 프로비저닝 스크립트 (2026-01-19)
# 기능: 도메인/DB/NGINX/WP 설치 자동화 (예: sudo bash scripts/vps/provision_site.sh --domain t1.zerotheme.com --admin-email admin@example.com)

set -euo pipefail

print_info() {
  # 사용자 안내 메시지를 출력한다.
  echo "[정보] $1"
}

print_error() {
  # 사용자에게 친절한 에러 메시지를 출력한다.
  echo "[오류] $1" 1>&2
}

require_root() {
  # 루트 권한이 필요하므로 체크한다.
  if [[ "${EUID}" -ne 0 ]]; then
    print_error "루트 권한이 필요합니다. sudo로 실행해주세요."
    exit 1
  fi
}

require_command() {
  # 필수 명령어가 존재하는지 확인한다.
  if ! command -v "$1" >/dev/null 2>&1; then
    print_error "필수 명령어를 찾을 수 없습니다: $1"
    exit 1
  fi
}

sanitize_identifier() {
  # DB 식별자를 안전하게 정규화한다.
  local raw_value="$1"
  local max_length="$2"
  local sanitized
  sanitized="$(echo "${raw_value}" | tr -cd '[:alnum:]_' | tr '[:upper:]' '[:lower:]')"
  if [[ -z "${sanitized}" ]]; then
    sanitized="site"
  fi
  echo "${sanitized:0:${max_length}}"
}

generate_password() {
  # 고정 비밀번호를 반환한다 (개발/테스트용).
  # 운영 환경에서는 랜덤 비밀번호 사용을 권장한다.
  echo "lqp1o2k3!"
}

detect_php_socket() {
  # PHP-FPM 소켓 경로를 자동 감지한다.
  local socket_path
  socket_path="$(ls /run/php/php*-fpm.sock 2>/dev/null | head -n 1 || true)"
  if [[ -z "${socket_path}" ]]; then
    print_error "PHP-FPM 소켓을 찾을 수 없습니다. php-fpm 설치를 확인해주세요."
    exit 1
  fi
  echo "${socket_path}"
}

usage() {
  # 사용법을 출력한다.
  cat <<EOF
사용법:
  sudo bash scripts/vps/provision_site.sh \\
    --domain t1.zerotheme.com \\
    --site-title "템플릿 사이트" \\
    --admin-user admin \\
    --admin-pass "StrongPass123!" \\
    --admin-email admin@example.com

옵션:
  --db-name        DB 이름 (미지정 시 도메인 기반 자동 생성)
  --db-user        DB 사용자 (미지정 시 도메인 기반 자동 생성)
  --db-pass        DB 비밀번호 (미지정 시 랜덤 생성)
  --wp-locale      WP 로케일 (기본값: ko_KR)
  --php-socket     PHP-FPM 소켓 경로 (미지정 시 자동 감지)
EOF
}

DOMAIN=""
SITE_TITLE="New WordPress Site"
ADMIN_USER="admin"
ADMIN_PASS=""
ADMIN_EMAIL=""
DB_NAME=""
DB_USER=""
DB_PASS=""
WP_LOCALE="ko_KR"
PHP_SOCKET=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --domain)
      DOMAIN="$2"
      shift 2
      ;;
    --site-title)
      SITE_TITLE="$2"
      shift 2
      ;;
    --admin-user)
      ADMIN_USER="$2"
      shift 2
      ;;
    --admin-pass)
      ADMIN_PASS="$2"
      shift 2
      ;;
    --admin-email)
      ADMIN_EMAIL="$2"
      shift 2
      ;;
    --db-name)
      DB_NAME="$2"
      shift 2
      ;;
    --db-user)
      DB_USER="$2"
      shift 2
      ;;
    --db-pass)
      DB_PASS="$2"
      shift 2
      ;;
    --wp-locale)
      WP_LOCALE="$2"
      shift 2
      ;;
    --php-socket)
      PHP_SOCKET="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      print_error "알 수 없는 옵션입니다: $1"
      usage
      exit 1
      ;;
  esac
done

require_root
require_command nginx
require_command wp
require_command mysql

if [[ -z "${DOMAIN}" || -z "${ADMIN_EMAIL}" || -z "${ADMIN_PASS}" ]]; then
  print_error "--domain, --admin-email, --admin-pass는 필수입니다."
  usage
  exit 1
fi

if [[ -z "${DB_NAME}" ]]; then
  DB_NAME="$(sanitize_identifier "${DOMAIN//./_}" 32)"
fi
if [[ -z "${DB_USER}" ]]; then
  DB_USER="$(sanitize_identifier "${DOMAIN//./_}" 16)"
fi
if [[ -z "${DB_PASS}" ]]; then
  DB_PASS="$(generate_password)"
fi
if [[ -z "${PHP_SOCKET}" ]]; then
  PHP_SOCKET="$(detect_php_socket)"
fi

SITE_ROOT="/var/www/wp-sites/${DOMAIN}"
PUBLIC_ROOT="${SITE_ROOT}/public"
LOG_ROOT="${SITE_ROOT}/logs"

print_info "디렉터리를 생성합니다: ${SITE_ROOT}"
mkdir -p "${PUBLIC_ROOT}" "${LOG_ROOT}"
chown -R www-data:www-data "${SITE_ROOT}"

print_info "DB를 생성합니다."
mysql -e "CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -e "CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';"
mysql -e "GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'localhost'; FLUSH PRIVILEGES;"

print_info "WordPress를 설치합니다."
wp core download --path="${PUBLIC_ROOT}" --locale="${WP_LOCALE}" --allow-root
wp config create \
  --path="${PUBLIC_ROOT}" \
  --dbname="${DB_NAME}" \
  --dbuser="${DB_USER}" \
  --dbpass="${DB_PASS}" \
  --dbhost="localhost" \
  --dbprefix="wp_" \
  --skip-check \
  --allow-root
wp core install \
  --path="${PUBLIC_ROOT}" \
  --url="http://${DOMAIN}" \
  --title="${SITE_TITLE}" \
  --admin_user="${ADMIN_USER}" \
  --admin_password="${ADMIN_PASS}" \
  --admin_email="${ADMIN_EMAIL}" \
  --skip-email \
  --allow-root

print_info "Nginx 가상호스트를 생성합니다."
NGINX_CONF="/etc/nginx/sites-available/${DOMAIN}"
cat > "${NGINX_CONF}" <<EOF
server {
    listen 80;
    server_name ${DOMAIN};
    root ${PUBLIC_ROOT};
    index index.php index.html;

    access_log ${LOG_ROOT}/access.log;
    error_log ${LOG_ROOT}/error.log;

    client_max_body_size 256M;

    location / {
        try_files \$uri \$uri/ /index.php?\$args;
    }

    location ~ \.php\$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:${PHP_SOCKET};
        fastcgi_read_timeout 300;
    }

    location ~* \.(jpg|jpeg|png|gif|ico|css|js|woff|woff2|ttf|svg)$ {
        expires max;
        log_not_found off;
    }
}
EOF

ln -s "${NGINX_CONF}" "/etc/nginx/sites-enabled/${DOMAIN}" 2>/dev/null || true
nginx -t
systemctl reload nginx

print_info "SSL 인증서를 발급합니다 (Let's Encrypt)."
if command -v certbot >/dev/null 2>&1; then
  certbot --nginx -d "${DOMAIN}" --non-interactive --agree-tos --email "${ADMIN_EMAIL}" --redirect || {
    print_error "SSL 발급 실패. DNS가 정상적으로 연결되었는지 확인해주세요."
  }
else
  print_error "certbot이 설치되어 있지 않습니다. 'sudo apt install -y certbot python3-certbot-nginx'로 설치해주세요."
fi

print_info "프로비저닝이 완료되었습니다."
echo "도메인: https://${DOMAIN}"
echo "WP 관리자: https://${DOMAIN}/wp-admin"
echo "DB 이름: ${DB_NAME}"
echo "DB 사용자: ${DB_USER}"
echo "DB 비밀번호: ${DB_PASS}"
