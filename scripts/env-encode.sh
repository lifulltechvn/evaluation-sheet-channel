#!/bin/bash
# =============================================================================
# env-encode.sh - Mã hóa (encrypt) file .env thành .env.encrypted
# Sử dụng AES-256-CBC với openssl
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="${PROJECT_ROOT}/.env"
ENCRYPTED_FILE="${PROJECT_ROOT}/.env.encrypted"

# Màu sắc cho output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== ENV Encoder (AES-256-CBC) ===${NC}"
echo ""

# Kiểm tra file .env tồn tại
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}[ERROR] File .env không tồn tại tại: ${ENV_FILE}${NC}"
    echo "Hãy tạo file .env trước khi encode."
    exit 1
fi

# Nhập passphrase
echo -n "Nhập passphrase để encrypt: "
read -s PASSPHRASE
echo ""

if [ -z "$PASSPHRASE" ]; then
    echo -e "${RED}[ERROR] Passphrase không được để trống.${NC}"
    exit 1
fi

# Xác nhận passphrase
echo -n "Xác nhận passphrase: "
read -s PASSPHRASE_CONFIRM
echo ""

if [ "$PASSPHRASE" != "$PASSPHRASE_CONFIRM" ]; then
    echo -e "${RED}[ERROR] Passphrase không khớp.${NC}"
    exit 1
fi

# Encrypt file .env
openssl enc -aes-256-cbc -salt -pbkdf2 -iter 100000 \
    -in "$ENV_FILE" \
    -out "$ENCRYPTED_FILE" \
    -pass "pass:${PASSPHRASE}"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}[SUCCESS] Đã encrypt thành công!${NC}"
    echo -e "  Input:  ${ENV_FILE}"
    echo -e "  Output: ${ENCRYPTED_FILE}"
    echo ""
    echo -e "${YELLOW}[NOTE] Bạn có thể push .env.encrypted lên repository.${NC}"
    echo -e "${YELLOW}       Team members dùng ./scripts/env-decode.sh để giải mã.${NC}"
else
    echo -e "${RED}[ERROR] Encrypt thất bại.${NC}"
    exit 1
fi
