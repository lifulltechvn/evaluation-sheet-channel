#!/bin/bash
# =============================================================================
# env-decode.sh - Giải mã (decrypt) file .env.encrypted thành .env
# Sử dụng AES-256-CBC với openssl
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENCRYPTED_FILE="${PROJECT_ROOT}/.env.encrypted"
ENV_FILE="${PROJECT_ROOT}/.env"

# Màu sắc cho output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== ENV Decoder (AES-256-CBC) ===${NC}"
echo ""

# Kiểm tra file .env.encrypted tồn tại
if [ ! -f "$ENCRYPTED_FILE" ]; then
    echo -e "${RED}[ERROR] File .env.encrypted không tồn tại tại: ${ENCRYPTED_FILE}${NC}"
    echo "Hãy pull code mới nhất từ repository."
    exit 1
fi

# Cảnh báo nếu .env đã tồn tại
if [ -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}[WARNING] File .env đã tồn tại. Nội dung sẽ bị ghi đè.${NC}"
    echo -n "Tiếp tục? (y/N): "
    read CONFIRM
    if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
        echo "Đã hủy."
        exit 0
    fi
    echo ""
fi

# Nhập passphrase
echo -n "Nhập passphrase để decrypt: "
read -s PASSPHRASE
echo ""

if [ -z "$PASSPHRASE" ]; then
    echo -e "${RED}[ERROR] Passphrase không được để trống.${NC}"
    exit 1
fi

# Decrypt file
openssl enc -aes-256-cbc -d -salt -pbkdf2 -iter 100000 \
    -in "$ENCRYPTED_FILE" \
    -out "$ENV_FILE" \
    -pass "pass:${PASSPHRASE}" 2>/dev/null

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}[SUCCESS] Đã decrypt thành công!${NC}"
    echo -e "  Input:  ${ENCRYPTED_FILE}"
    echo -e "  Output: ${ENV_FILE}"
    echo ""
    echo -e "${YELLOW}[NOTE] File .env đã sẵn sàng sử dụng.${NC}"
    echo -e "${YELLOW}       KHÔNG push file .env lên repository.${NC}"
else
    echo -e "${RED}[ERROR] Decrypt thất bại. Passphrase có thể không đúng.${NC}"
    # Xóa file output lỗi nếu có
    rm -f "$ENV_FILE"
    exit 1
fi
