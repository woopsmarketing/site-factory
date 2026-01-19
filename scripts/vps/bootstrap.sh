#!/usr/bin/env bash
# v0.1 - VPS 기본 패키지 설치 스크립트 (2026-01-16)
# 기능: Ubuntu 22.04 기준으로 필수 패키지 설치 (예: sudo bash scripts/vps/bootstrap.sh)

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

check_ubuntu_version() {
  # Ubuntu 22.04 환경인지 확인한다.
  if [[ ! -f /etc/os-release ]]; then
    print_error "/etc/os-release 파일을 찾을 수 없습니다."
    exit 1
  fi

  local version_id
  version_id="$(. /etc/os-release && echo "${VERSION_ID}")"
  if [[ "${version_id}" != "22.04" ]]; then
    print_error "이 스크립트는 Ubuntu 22.04 기준입니다. 현재 버전: ${version_id}"
    exit 1
  fi
}

install_packages() {
  # 필수 패키지를 설치한다.
  print_info "패키지 목록을 갱신합니다."
  apt-get update -y

  print_info "Nginx, PHP, MariaDB 등 필수 패키지를 설치합니다."
  apt-get install -y \
    nginx \
    mariadb-server \
    curl \
    unzip \
    jq \
    php-fpm \
    php-mysql \
    php-xml \
    php-curl \
    php-gd \
    php-mbstring \
    php-zip
}

install_wp_cli() {
  # WP-CLI가 없다면 설치한다.
  if command -v wp >/dev/null 2>&1; then
    print_info "WP-CLI가 이미 설치되어 있습니다."
    return
  fi

  print_info "WP-CLI를 설치합니다."
  curl -sSL https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar -o /tmp/wp-cli.phar
  chmod +x /tmp/wp-cli.phar
  mv /tmp/wp-cli.phar /usr/local/bin/wp
}

prepare_directories() {
  # 사이트 루트 디렉터리를 준비한다.
  local base_dir="/var/www/wp-sites"
  if [[ ! -d "${base_dir}" ]]; then
    print_info "사이트 루트 디렉터리를 생성합니다: ${base_dir}"
    mkdir -p "${base_dir}"
  else
    print_info "사이트 루트 디렉터리가 이미 존재합니다: ${base_dir}"
  fi
}

main() {
  require_root
  check_ubuntu_version
  install_packages
  install_wp_cli
  prepare_directories
  print_info "기본 환경 구성이 완료되었습니다."
}

main "$@"
