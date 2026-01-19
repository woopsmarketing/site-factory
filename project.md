# WordPress Site Factory (UiCore + Elementor) — Automation Blueprint
> 목적: VPS 1대에서 여러 워드프레스 사이트를 “템플릿 기반 + 완전 자동 커스터마이징”으로 생성한다.  
> 전제: UiCore(Theme) + Elementor(필수), ElementsPack Pro + Elementor Pro 사용, SEO는 RankMath로 고정, 단일 언어(ko/en 중 1개), 이미지/OG까지 자동 생성, 디자인 토큰(색/폰트/아이콘/이미지 톤) 강제.

---

## 0. 핵심 목표(Outcome)
- **입력값 4~6개만으로** 신규 도메인에 완성된 WP 사이트를 자동 생성한다.
- **레이아웃은 템플릿을 유지**하되, 사이트의 다음 요소는 반드시 “독립적으로” 생성/치환한다:
  - 사이트 아이덴티티(브랜드명/타이틀/로고/파비콘/연락처/정책)
  - 디자인 토큰(색/폰트/아이콘 세트/이미지 톤)
  - 콘텐츠(모든 텍스트/FAQ/CTA/풋터 문구 등)
  - SEO(페이지별 title/description/OG/Organization 스키마/robots/sitemap 정책)
  - 내부 URL/링크(버튼/메뉴/CTA/이미지 링크/절대 URL 포함)
- 템플릿이 30개로 늘어나도 범용으로 돌아가도록 **공통 스펙(site_spec.json) + 템플릿 어댑터(template_adapter.json)** 구조로 설계한다.

---

## 1. 시스템 아키텍처 개요
### 1.1 구성요소
- **Python Orchestrator (CLI/Service)**
  - 전체 파이프라인 실행, 상태 관리, 로그, 재시도, 검증 포함
- **WordPress on VPS**
  - Nginx + PHP-FPM + MariaDB
  - WP-CLI로 설치/설정 자동화
- **Elementor/UiCore**
  - 템플릿 Kit/Export import 후 Elementor 데이터(JSON)를 어댑터 기반으로 치환
- **RankMath**
  - SEO 메타 및 스키마/사이트맵/robots 설정 자동화
- **Cloudflare**
  - DNS 레코드 및 프록시 설정(필요 시) 자동화
- **LLM**
  - site_spec.json 생성(브랜드/카피/SEO/이미지 요구사항)
- **Image Generation**
  - 히어로/섹션 이미지/아이콘/OG 이미지 생성 및 WP 미디어 업로드

---

## 2. 파이프라인 입력값(Step 0)
### 2.1 최소 입력값(권장)
- `domain`: 신규 도메인 (예: example.com)
- `template_id`: t1~t30 중 하나
- `language`: ko 또는 en (단일 언어)
- `niche_topic`: 사이트 주제 (예: “AI SEO SaaS”, “Interior Design Studio”)

### 2.2 선택 입력값(품질 향상)
- `target_keywords`: 핵심 키워드 리스트
- `target_money_url`: 주요 CTA 목적지 URL (없으면 사이트 내 문의/구독 페이지로)
- `brand_style_hint`: 톤/캐릭터 힌트 (예: “신뢰감, 미니멀, 프리미엄”)
- `region_hint`: 지역 기반 비즈니스일 경우(없으면 글로벌)

> 입력값은 최소화하고, 나머지는 LLM이 `site_spec.json`으로 자동 생성한다.

---

## 3. 파이프라인 단계(Step 1~8) 상세

## STEP 1. 인프라 + 워드프레스 자동 설치(결정론)
### 1.1 서버 리소스 생성/할당
- Nginx vhost 생성 (템플릿 기반)
- PHP-FPM pool (가능하면 사이트별 pool 생성)
- DB 생성 + DB 유저 생성 + 권한 부여
- 사이트별 디렉토리 생성 + 권한/소유자 분리

### 1.2 WP 설치 및 기본 세팅
- WP-CLI로 워드프레스 설치:
  - `siteurl/home` 설정(신규 도메인)
  - timezone, permalink 구조, 기본 옵션 설정
  - 관리자 계정 생성(안전한 비밀번호)
- 필수 플러그인 설치/활성:
  - Elementor Pro
  - ElementsPack Pro
  - RankMath
  - 캐시 플러그인(고정 선택)
  - (필요 시) 이미지 최적화/리사이즈 플러그인
- UiCore 테마 설치 및 활성화
- (필요 시) 라이선스 키/활성화 처리(자동 또는 사전 세팅)

### 1.3 결과
- 새 도메인에서 **빈 워드프레스가 정상 구동**되고, 필수 플러그인이 활성화된 상태

---

## STEP 2. 템플릿 주입(Kit/Export Import)
### 2.1 템플릿 관리 규칙
- 템플릿 30개는 `template_id` 별로 **Kit/Export 파일**로 관리한다.
- 템플릿 패키지에는 최소 다음이 포함되어야 한다:
  - Elementor Kit/템플릿
  - 필수 페이지(홈/서비스/어바웃/문의 등) 생성 구성
  - 헤더/푸터 템플릿(Theme Builder 사용 시)

### 2.2 적용 절차
- `template_id`에 해당하는 Kit/Export 파일을 import
- 필요한 페이지가 자동 생성되었는지 확인:
  - 홈 1개 + 평균 5페이지(템플릿마다 상이)
- (필요 시) 홈 페이지를 Front Page로 지정

### 2.3 결과
- **템플릿 그대로 복제된 사이트가 일단 뜬 상태**(복제티 존재)

---

## STEP 3. site_spec.json 생성(LLM)
### 3.1 site_spec.json이 담아야 할 것(필수)
LLM이 아래를 기반으로 **완성된 사이트 스펙 JSON**을 생성한다:

#### (A) 브랜드/아이덴티티
- `brand.name`
- `brand.tagline`
- `brand.tone` (예: friendly/professional/premium 등)
- `brand.logo_prompt` (또는 logo asset 지정 방식)
- `brand.contact` (email/phone/address 등)

#### (B) 디자인 토큰(강제)
- `design.colors` (primary/secondary/accent + bg/text/border 등)
- `design.fonts` (heading/body)
- `design.icon_style` (라인/필드/3D 등)
- `design.image_style` (사진/일러스트/3D/그레인 등 톤 정의)

#### (C) 콘텐츠(페이지별)
- 홈 및 주요 페이지별:
  - hero(H1/sub/CTA)
  - 가치제안(Why us 3~6개)
  - 서비스/기능 섹션
  - FAQ(Q/A)
  - footer 문구/정책 링크 텍스트
- 텍스트뿐 아니라 **alt 텍스트**까지 생성

#### (D) SEO(페이지별 + 사이트단위)
- 각 페이지:
  - `seo.title`, `seo.description`
  - OG(Twitter/FB) 메타 텍스트
  - OG 이미지 프롬프트
- 사이트단위:
  - Organization 스키마: name/url/logo/sameAs
  - robots/sitemap 정책(필요 최소)

#### (E) 사이트 구조
- 메뉴 구조(라벨/대상 슬러그)
- 카테고리 5~12개 (블로그 운영 시)
- CTA 목적지

### 3.2 결과
- “이 사이트는 무엇인가”에 대한 **완성 스펙**이 `site_spec.json`으로 생성됨

---

## STEP 4. 이미지 생성/업로드(자동)
### 4.1 이미지 목록 추출
- site_spec에서 필요한 이미지 요구사항을 추출:
  - hero 이미지
  - 섹션 배경/일러스트
  - 아이콘/패턴(필요 시)
  - OG 대표 이미지

### 4.2 생성 → 업로드 → 매핑
- 이미지 생성(정의된 톤 유지)
- 워드프레스 미디어 라이브러리 업로드
- 업로드 후 다음을 매핑 테이블로 저장:
  - `image_key -> { media_id, url, width, height, alt }`

### 4.3 리사이즈/썸네일 처리
- WP의 이미지 리사이즈/썸네일 자동 생성 확인
- 필요 시 썸네일 재생성 트리거

### 4.4 결과
- 사이트에 사용될 이미지 리소스가 **URL 및 media_id까지 확보된 상태**

---

## STEP 5. template_adapter.json 기반 Elementor 주입(핵심)
> 템플릿마다 구조가 달라도 범용으로 돌리기 위한 “지도”가 template_adapter.json이다.  
> adapter는 **전체 JSON을 들고 있는 게 아니라**, “교체 포인트(Patch) 목록”만 들고 있어야 유지보수가 된다.

### 5.1 어댑터의 역할
- 특정 템플릿의 특정 페이지에서,
  - 어떤 element_id의
  - 어떤 path(settings.* 등)에
  - site_spec의 어떤 key 값을
  - 어떤 op(set_text/set_html/set_url/set_image_url 등)로 넣을지
정의한다.

### 5.2 권장 adapter 구조(개념)
- `template_id`
- `pages`:
  - 각 페이지별 `post_slug` 또는 페이지 식별자
  - `patches`:
    - `{ key, element_id, path, op }`
- `globals`:
  - Global Kit 색/폰트 매핑(가능하면 템플릿 공통으로 적용)

### 5.3 주입 엔진 동작
1. 대상 페이지의 Elementor 데이터(JSON)를 가져온다.
2. adapter의 patches를 순회하며 site_spec 값을 찾아 지정된 path에 주입한다.
3. 변경된 Elementor JSON을 저장한다.
4. (가능하면) Global Kit(색/폰트)도 별도 경로로 적용한다.

### 5.4 결과
- 레이아웃은 그대로지만,
- 텍스트/이미지/링크/색/폰트가 전부 바뀐 “새 사이트”가 된다.

---

## STEP 6. RankMath SEO 주입
### 6.1 페이지별 메타
- site_spec의 페이지별 SEO 데이터를 RankMath에 주입:
  - title / description
  - OG 메타 + OG 이미지

### 6.2 사이트단위 설정
- Organization 스키마(브랜드명/URL/로고/소셜)
- sitemap 활성화 및 포함 범위
- robots 기본 정책

### 6.3 결과
- SEO 메타까지 사이트별로 완전히 다르게 설정됨

---

## STEP 7. URL 치환 + CSS 재생성 + 캐시 플러시
### 7.1 도메인 흔적 제거(필수)
- 템플릿 import 후 남는 절대 URL 제거:
  - 버튼 링크
  - 메뉴 링크
  - 이미지 링크
  - 폰트/아이콘/배경 이미지 경로
- `wp search-replace`로 이전 도메인 흔적을 신규 도메인으로 치환

### 7.2 빌더/테마 캐시 재생성
- Elementor CSS regenerate/flush
- UiCore 캐시 flush
- 캐시 플러그인 flush
- 퍼머링크 flush

### 7.3 결과
- 잔여 링크/리소스 깨짐 최소화 + 변경사항 적용 완료

---

## STEP 8. Smoke Test(자동 점검)
### 8.1 HTTP 기본 점검
- 주요 페이지 HTTP 200 확인:
  - 홈 + 주요 4~5페이지
- 내부 링크 404 체크(핵심 링크 우선)
- 이미지 누락 체크(대표 이미지/히어로 우선)

### 8.2 SEO 점검(간단 파싱)
- OG 태그 존재 여부
- title/description 세팅 존재 여부
- RankMath 적용 여부 확인(메타 출력 확인)

### 8.3 디자인 토큰 적용 점검(간단)
- 대표 색상(primary) 적용 흔적 확인
- heading/body 폰트 적용 여부 확인

### 8.4 결과
- 자동 배포 품질을 기본적으로 보장

---

## 4. 데이터 계약서(Contracts)

## 4.1 site_spec.json (Contract)
### 4.1.1 필수 키(모든 사이트에서 반드시 존재)
- `brand.name`
- `brand.tagline`
- `brand.contact.email`
- `design.colors.primary`
- `design.colors.secondary`
- `design.colors.accent`
- `design.fonts.heading`
- `design.fonts.body`
- `pages.home.hero.h1`
- `pages.home.hero.sub`
- `pages.home.hero.cta_text`
- `pages.home.hero.cta_url`
- `seo.home.title`
- `seo.home.description`
- `seo.organization.name`
- `seo.organization.url`

### 4.1.2 선택 키(템플릿마다 존재하면 채우고 없으면 스킵)
- `pages.*.sections.*` (서비스/기능/소개/케이스 등)
- `faq[]`
- `testimonials[]`
- `categories[]`
- `menu[]`
- 이미지 상세 세트(섹션별)

---

## 4.2 template_adapter.json (Contract)
### 4.2.1 설계 원칙
- adapter는 “전체 Elementor JSON”을 담지 않는다.
- **교체 포인트(Patch) 목록만** 가진다.
- 템플릿당 1회 제작 후 재사용한다.

### 4.2.2 최소 필수 매핑(권장)
각 템플릿은 최소 아래는 매핑되어야 한다:
- 홈 hero_h1 / hero_sub / CTA text+url / hero image
- 헤더 메뉴(또는 메뉴 생성 규칙)
- 푸터 연락처/정책 링크/카피라이트 문구
- Global colors + fonts 적용 포인트(가능하면)

### 4.2.3 op(연산) 표준
- `set_text`: 일반 텍스트 주입
- `set_html`: HTML/리치텍스트 주입
- `set_url`: 링크 URL 주입
- `set_image_url`: 이미지 URL 주입
- `set_media_id`: media_id 기반 주입(필요 시)
- `delete`: 특정 위젯/섹션 제거(예: testimonials 없으면 제거)

---

## 5. 템플릿 방대한 Elementor JSON 다루는 전략

## 5.1 사람이 직접 읽지 않는다(금지)
- Elementor JSON은 방대하고 구조가 템플릿마다 다르므로,
- 인간은 JSON을 직접 분석하지 않고, **스캐너(scanner)**가 만들어낸 manifest로 작업한다.

## 5.2 Template Scanner(필수 개발 컴포넌트)
템플릿별 1회 작업을 “선별 작업”으로 만들기 위한 도구.

### 5.2.1 입력
- 템플릿별 Elementor JSON fixtures:
  - `fixtures/t12/home.elementor.json`
  - `fixtures/t12/about.elementor.json`
  - ...

### 5.2.2 출력
- `manifest.json`:
  - 페이지별 위젯 타입 분포
  - 텍스트/링크/이미지 후보 리스트
  - 후보마다 `{ element_id, widget_type, path, preview }`
- `adapter_skeleton.json`:
  - 후보 patch 리스트(초안)

### 5.2.3 휴리스틱 추천(자동 후보 선정)
- “hero_h1” 후보: 상단 섹션에서 가장 큰 heading 또는 가장 긴 heading
- “CTA” 후보: 버튼 위젯 중 가장 상단 위치
- “hero_image” 후보: 상단 이미지 위젯
- footer/contact 후보: 페이지 하단 텍스트 위젯 중 email/phone 패턴 포함

> 목표: 템플릿 30개라도 “사람이 하는 일”은 후보 선택/확정만 하도록.

---

## 6. 개발 환경/워크플로우(권장)

## 6.1 로컬(Cursor) 중심 + VPS 통합테스트
- 로컬: Python 코드 개발, fixtures 기반 유닛테스트, adapter 생성 자동화
- VPS: 실제 WordPress/Elementor/RankMath 환경에서 E2E 테스트

## 6.2 버전관리/배포
- Git을 기준으로 관리:
  - 로컬에서 커밋/푸시
  - VPS에서 `git pull`
- VPS에는 `.env`(API 키/DB 루트/Cloudflare 토큰 등)만 별도 보관

## 6.3 테스트 전략
- Unit Test:
  - Elementor patcher가 fixtures JSON에 정상 주입되는지
  - adapter/schema validation
- Integration Test (VPS):
  - 실제 WP에 적용 후 페이지 렌더 결과/메타 반영 여부 확인

---

## 7. Python 구현 범위(모듈 설계)

### 7.1 Orchestrator
- `create_site(domain, template_id, language, niche_topic, ...)` 단일 엔트리
- 단계별 실행 + 실패 시 롤백/재시도 옵션
- 실행 로그 + 결과 리포트(JSON/HTML)

### 7.2 Contracts
- site_spec 스키마 검증(필수키 존재, 타입 체크)
- adapter 스키마 검증(중복 patch, 잘못된 path 탐지)

### 7.3 Elementor
- `scanner`: JSON에서 교체 후보 추출 → manifest 생성
- `patcher`: adapter patches를 적용 → Elementor JSON 저장

### 7.4 WordPress
- wp-cli 래퍼:
  - 설치/설정/플러그인/테마
  - search-replace, permalink flush
  - elementor CSS regenerate(가능하면 wp-cli 또는 내부 트리거)

### 7.5 SEO (RankMath)
- 페이지별 메타 주입(메타키 기반 또는 API 기반)
- Organization/robots/sitemap 설정

### 7.6 Media
- 이미지 생성 요청 생성(프롬프트)
- 이미지 업로드/alt 설정
- media_id/url 매핑 저장

### 7.7 Smoke Test
- HTTP 상태 점검
- 내부 링크/이미지 누락 점검
- OG/meta 존재 확인

---

## 8. 실행 결과물(산출물)
- `site_spec.json` (사이트 스펙)
- `template_adapter.json` (템플릿 지도)
- `run_report.json` (단계별 결과/시간/에러/재시도 로그)
- (선택) `run_report.html` (사람이 보기 쉬운 리포트)

---

## 9. 운영 시 주의사항(필수)
- 사이트별 고유키:
  - Analytics/픽셀/SMTP/reCAPTCHA 등은 사이트별로 분리
- 서버 격리:
  - 디렉토리 권한 분리
  - 가능하면 PHP-FPM pool 분리
  - 로그/백업 분리
- 템플릿 확장:
  - 템플릿 추가는 **adapter + manifest만 추가**하는 형태로 유지

---

## 10. MVP 진행 순서(강력 권장)
1) 템플릿 t1 + 홈 1페이지에서:
   - hero_h1 / hero_sub / CTA / hero_image / primary_color / heading_font
   - 이 6개만 adapter로 주입 성공시키기
2) 페이지를 5개로 확장
3) RankMath SEO 주입 추가
4) 이미지 생성/업로드 + OG 자동 생성
5) 템플릿 t2, t3를 추가하여 adapter 범용성 검증
6) 최종적으로 t1~t30 확장

---

## 부록: “독립성”을 위한 필수 교체 목록(요약)
- Site Title/Tagline
- home/siteurl
- 로고/파비콘/OG 기본 이미지
- 브랜드명/슬로건/연락처
- 홈/주요 페이지 title/meta description
- Organization 스키마(name/url/logo/sameAs)
- robots/sitemap 정책
- 버튼/메뉴/CTA/이미지 링크 포함 내부 URL 전부
- 디자인 토큰(색/폰트/아이콘/이미지 톤)
- 모든 텍스트 콘텐츠(히어로/FAQ/풋터 등)
- alt 텍스트

---
