#!/bin/bash
# 백업 복원 스크립트
# 사용: bash scripts/vps/restore_backup.sh <backup_file> [page_id]

set -e

BACKUP_FILE=${1}
PAGE_ID=${2:-62}
WP_PATH=/var/www/wp-sites/t1.zerotheme.co.kr/public

if [ -z "$BACKUP_FILE" ]; then
    echo "❌ 사용법: bash scripts/vps/restore_backup.sh <backup_file> [page_id]"
    echo ""
    echo "📦 사용 가능한 백업:"
    ls -lh /opt/site-factory/backups/
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ 백업 파일을 찾을 수 없습니다: $BACKUP_FILE"
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔙 백업 복원"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📦 백업 파일: $BACKUP_FILE"
echo "📄 페이지 ID: $PAGE_ID"
echo ""

read -p "복원하시겠습니까? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 취소됨"
    exit 0
fi

echo ""
echo "🔄 복원 중..."

cd $WP_PATH
sudo -u www-data wp post meta update $PAGE_ID _elementor_data "$(cat $BACKUP_FILE)" --allow-root

echo "   ✅ DB 복원 완료"

echo ""
echo "🎨 CSS 재생성 중..."
sudo -u www-data wp elementor flush-css --allow-root
sudo -u www-data wp cache flush --allow-root

echo "   ✅ CSS 재생성 완료"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 복원 완료!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 웹사이트 확인:"
echo "   https://t1.zerotheme.co.kr"
echo ""
