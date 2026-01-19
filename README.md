# WordPress Site Factory - 자동화 스캐폴딩

이 저장소는 `project.md`의 자동화 설계를 실행 가능한 코드로 옮기기 위한 초기 스캐폴딩입니다.  
현재는 **Mock 데이터 기반 파이프라인 실행**과 **어댑터/스펙 검증 뼈대**까지 포함합니다.

## 빠른 시작 (로컬, Windows 기준)
1) 가상환경 생성/활성화
```
python -m venv venv
.\venv\Scripts\activate
```

2) 소스 경로 추가 (개발 편의)
```
set PYTHONPATH=src
```

3) Mock 파이프라인 실행
```
python -m site_factory.cli run --use-mock --config config.sample.json --output-dir output
```

## Elementor 스캐너 사용
```
python -m site_factory.cli scan --input data/mock/elementor.sample.json --output-dir output --page-slug home --template-id t1
```

### 실행 결과
- `output/patched_elementor.json`: 어댑터 적용 결과
- `output/patch_results.json`: 패치 결과 상세
- `output/run_report.json`: 실행 리포트

## 설정 파일
- `config.sample.json`을 복사해서 `config.local.json` 등으로 사용하세요.
- `.env`는 사용하지 않습니다.

## 문서
- 환경 구성 가이드: `docs/ENV_SETUP.md`
- 설계 문서: `project.md`
