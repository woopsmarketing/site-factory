# CSS ID 컨벤션 (템플릿 공통)

## 네이밍 규칙
- 기본 형식: `{section}_{type}_{index}`
- 같은 타입 섹션이 여러 개: `{section}_{number}_{type}_{index}`
- 소문자 + 언더스코어
- 명확하고 일관성 있게

### 예시:
```
hero_title              # Hero 섹션 제목
features_card_1         # Features 섹션 카드 1
features_2_card_1       # 두 번째 Features 섹션 카드 1
pricing_card_1          # Pricing 섹션 카드 1
```

---

## 섹션 타입 가이드

### 필수 섹션 (대부분 템플릿에 있음)
- `hero` - 히어로/메인 섹션
- `features` - 기능/서비스 소개
- `pricing` - 가격 정보
- `cta` - 행동 유도

### 선택 섹션 (있을 수도, 없을 수도)
- `about` - 회사 소개
- `testimonial` - 고객 후기
- `stats` - 통계/숫자
- `team` - 팀 소개
- `portfolio` - 포트폴리오
- `blog` - 블로그
- `contact` - 연락처
- `faq` - FAQ

### 같은 타입이 여러 개일 경우
```
features_1_title        # 첫 번째 Features 섹션
features_1_card_1

features_2_title        # 두 번째 Features 섹션
features_2_card_1

cta_1_title            # 첫 번째 CTA
cta_2_title            # 두 번째 CTA (페이지 하단)
```

---

## Hero 섹션 (필수)
```
hero_title          # 메인 제목
hero_subtitle       # 부제목/강조 텍스트
hero_desc           # 설명문
hero_btn_primary    # 주요 CTA 버튼
hero_btn_secondary  # 보조 버튼
hero_img_main       # 메인 이미지
hero_img_1          # 추가 이미지 1
hero_img_2          # 추가 이미지 2
hero_img_3          # 추가 이미지 3
hero_badge          # 배지/아이콘
hero_text_small     # 부가 설명
```

---

## Features 섹션
```
features_title      # 섹션 제목
features_subtitle   # 섹션 부제목
features_desc       # 섹션 설명

# 카드 전체 (Icon Box, Feature Box 등)
features_card_1
features_card_2
features_card_3
features_card_4
features_card_5
features_card_6

# 또는 세분화
features_icon_1
features_title_1
features_desc_1
features_btn_1
```

---

## About 섹션
```
about_title
about_subtitle
about_desc
about_img_main
about_list
about_btn
```

---

## Pricing 섹션
```
pricing_title
pricing_subtitle
pricing_desc

pricing_card_1      # Basic
pricing_card_2      # Pro
pricing_card_3      # Enterprise
pricing_card_4      # Custom (있는 경우)
```

---

## Testimonial 섹션
```
testimonial_title
testimonial_subtitle

testimonial_card_1
testimonial_card_2
testimonial_card_3
testimonial_card_4
```

---

## Stats/Numbers 섹션
```
stats_title
stats_subtitle

stats_item_1        # 예: 97.5% - Customer satisfaction
stats_item_2        # 예: 130+ - Projects Completed
stats_item_3        # 예: 55M - Revenue Generated
stats_item_4
```

---

## Team 섹션
```
team_title
team_subtitle
team_desc

team_card_1
team_card_2
team_card_3
team_card_4
```

---

## Contact/CTA 섹션
```
contact_title
contact_subtitle
contact_desc
contact_btn
contact_form        # 폼 전체 (있는 경우)

cta_title
cta_subtitle
cta_desc
cta_btn_primary
cta_btn_secondary
cta_img
```

---

## Portfolio 섹션
```
portfolio_title
portfolio_subtitle
portfolio_desc

portfolio_card_1
portfolio_card_2
portfolio_card_3
portfolio_card_4
portfolio_card_5
portfolio_card_6
```

---

## Blog 섹션
```
blog_title
blog_subtitle
blog_desc

blog_card_1
blog_card_2
blog_card_3
blog_card_4
```

---

## FAQ 섹션
```
faq_title
faq_subtitle
faq_desc

faq_item_1
faq_item_2
faq_item_3
faq_item_4
faq_item_5
```

---

## Footer (선택)
```
footer_logo
footer_desc
footer_copyright
footer_social
footer_menu_1
footer_menu_2
footer_menu_3
footer_contact
```

---

## 작업 순서
1. 페이지 열기 (Elementor 편집기)
2. Navigator (Structure) 패널 열기
3. 섹션별로 위에서 아래로 작업
4. 핵심 위젯만 CSS ID 지정 (전체 아님)
5. 저장

## t1 템플릿 Home 페이지 CSS ID 체크리스트

### 섹션 1: Hero + Stats
```
□ hero_title           - "웹사이트 제작 최적화"
□ hero_subtitle        - "전문가부터 초보자까지 모두가 사용 가능한"
□ hero_desc            - "가장 완벽한 구성의 검증된 템플릿"
□ hero_btn             - "Explore"

□ stats_item_1         - 97.5% (Counter + Label 전체)
□ stats_item_2         - 130+
□ stats_item_3         - 55M
```

### 섹션 2: Features (서비스 카드)
```
□ features_title       - "나에게 필요한 템플릿을 찾아보세요"
□ features_subtitle    - "수십가지의 템플릿중 내가 원하는 레이아웃만"
□ features_desc        - "선택하세요 그리고 톤 변경 컨텐츠 삽입하면 끝!"

□ features_card_1      - Email Marketing 전체
□ features_card_2      - Content Marketing 전체
□ features_card_3      - Paid Campaigns 전체
□ features_card_4      - Brand Marketing 전체
□ features_card_5      - Social Media 전체
```

### 섹션 3: Pricing
```
□ pricing_title        - "템플릿 가격"
□ pricing_subtitle     - "기존 웹사이트 제작비용 90%이상 절약"

□ pricing_card_1       - Basic 전체
□ pricing_card_2       - Premium 전체
□ pricing_card_3       - Business 전체
```

### 섹션 4: Testimonial (고객 후기)
```
□ testimonial_title    - "고객분들이 남겨주신 소중한 리뷰"
□ testimonial_subtitle - "290+ 이상의 리뷰가 있습니다."

□ testimonial_card_1   - Tailwind 후기
□ testimonial_card_2   - HubSpot 후기
```

### 섹션 5: CTA (최종 행동 유도)
```
□ cta_title            - "우리 90%와 함께라면 업무 효율은 올라가고..."
□ cta_subtitle         - "템플릿만 고르시면 됩니다"
□ cta_btn              - "템플릿 보러가기"
□ cta_text_small       - "매뉴얼한 보고 따라하면 하루만에 완성됩니다!"
```

**총: 약 25개 (10~15분 작업)**

---

## 주의사항
- ❌ 모든 위젯에 CSS ID 지정하지 말 것
- ✅ 콘텐츠 주입이 필요한 핵심 위젯만
- ✅ 템플릿 30개 모두 같은 규칙 사용
- ✅ 페이지당 10~20개 정도면 충분
