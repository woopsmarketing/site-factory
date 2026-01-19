# 환경 구성 가이드 (로컬 + VPS)

## 1) 로컬 개발 환경 (Windows 기준)
### 1.1 Python 준비
- Python 3.10+ 설치 권장
- 가상환경 생성/활성화
```
python -m venv venv
.\venv\Scripts\activate
```

### 1.2 실행 경로 설정
- 소스 디렉터리를 PYTHONPATH에 추가
```
set PYTHONPATH=src
```

### 1.3 Mock 파이프라인 실행
```
python -m site_factory.cli run --use-mock --config config.sample.json --output-dir output
```

## 2) VPS 환경 (Ubuntu 22.04 기준)
### 2.1 기본 패키지
- Nginx
- PHP-FPM (8.1 권장)
- MariaDB
- WP-CLI
- 기타: curl, unzip, jq

### 2.2 자동 설치 스크립트
- `scripts/vps/bootstrap.sh`를 참고하세요.
```
sudo bash scripts/vps/bootstrap.sh
```

### 2.3 워드프레스 사이트 루트 구조(권장)
- `/var/www/wp-sites/{domain}/public`
- `/var/www/wp-sites/{domain}/logs`

### 2.4 WP Migrate 기반 복제
- 플러그인 설치 후, 템플릿 사이트를 Export/Import 방식으로 복제
- 복제 이후 도메인 치환은 `wp search-replace`로 처리 권장

## 3) 운영 시 보안 메모
- `.env`는 사용하지 않습니다.
- 실제 운영 키/비밀번호는 `config.local.json` 등 별도 파일로 관리하세요.
