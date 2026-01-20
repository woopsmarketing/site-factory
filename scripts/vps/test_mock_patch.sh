#!/bin/bash
#!/bin/bash
# v1.1 - 대용량 메타 업데이트 방식 개선 (2026.01.20)
# Mock 데이터 테스트 스크립트
# 사용 예시: bash scripts/vps/test_mock_patch.sh <page_id> <patched_json_path>

set -e

PAGE_ID=${1:-62}
PATCHED_JSON=${2:-/tmp/patched_elementor.json}
WP_PATH=/var/www/wp-sites/t1.zerotheme.co.kr/public
BACKUP_DIR=/opt/site-factory/backups

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 Mock 데이터 테스트"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. 백업 생성
echo ""
echo "📦 1. 백업 생성 중..."
mkdir -p $BACKUP_DIR
BACKUP_FILE="$BACKUP_DIR/elementor-backup-$(date +%Y%m%d-%H%M%S).json"

cd $WP_PATH
# 한글: 원본 Elementor JSON을 백업 파일로 저장합니다.
sudo -u www-data wp post meta get $PAGE_ID _elementor_data --allow-root > $BACKUP_FILE

echo "   ✅ 백업 완료: $BACKUP_FILE"

# 2. Mock 데이터 적용
echo ""
echo "🔄 2. Mock 데이터 적용 중..."
# 한글: 대용량 JSON을 안전하게 반영하기 위해 wp eval로 파일을 읽어 업데이트합니다.
sudo -u www-data wp eval "update_post_meta($PAGE_ID, '_elementor_data', file_get_contents('$PATCHED_JSON'));" --allow-root

echo "   ✅ DB 업데이트 완료"

# 3. Elementor CSS 재생성
echo ""
echo "🎨 3. CSS 재생성 중..."
# 한글: Elementor CSS와 캐시를 재생성합니다.
sudo -u www-data wp elementor flush-css --allow-root
sudo -u www-data wp cache flush --allow-root

echo "   ✅ CSS 재생성 완료"

# 4. 확인 안내
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Mock 데이터 적용 완료!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 웹사이트에서 확인하세요:"
echo "   https://t1.zerotheme.co.kr"
echo ""
echo "📝 백업 파일:"
echo "   $BACKUP_FILE"
echo ""
echo "🔙 복원하려면:"
echo "   sudo -u www-data wp eval \"update_post_meta($PAGE_ID, '_elementor_data', file_get_contents('$BACKUP_FILE'));\" --allow-root --path=$WP_PATH"
echo "   sudo -u www-data wp elementor flush-css --allow-root --path=$WP_PATH"
echo ""
