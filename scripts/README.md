# Scripts - Quản lý biến môi trường (Environment Variables)

## Tổng quan

Hệ thống encode/decode sử dụng **AES-256-CBC** (openssl) để mã hóa file `.env`, cho phép chia sẻ API keys và secrets an toàn qua repository.

## Yêu cầu

- `openssl` (có sẵn trên macOS/Linux)

## Workflow

### Người encode (người có secrets gốc)

```bash
# 1. Tạo/cập nhật file .env với các giá trị thực
# 2. Chạy encode
./scripts/env-encode.sh

# 3. Nhập passphrase (chia sẻ passphrase qua kênh riêng: Slack DM, etc.)
# 4. Commit và push .env.encrypted
git add .env.encrypted
git commit -m "chore: cập nhật env encrypted"
git push
```

### Người decode (team members)

```bash
# 1. Pull code mới nhất
git pull

# 2. Chạy decode
./scripts/env-decode.sh

# 3. Nhập passphrase (nhận từ người encode qua kênh riêng)
# 4. File .env sẽ được tạo tự động
```

## Lưu ý bảo mật

- **KHÔNG** push file `.env` lên repository
- **KHÔNG** chia sẻ passphrase qua commit message hoặc comment
- Chia sẻ passphrase qua kênh bảo mật (Slack DM, gặp trực tiếp, etc.)
- Khi thay đổi secrets, chạy lại `env-encode.sh` và thông báo team
- Passphrase nên có ít nhất 12 ký tự, bao gồm chữ hoa, chữ thường, số và ký tự đặc biệt

## Thông số kỹ thuật

| Thuộc tính | Giá trị |
|------------|---------|
| Algorithm | AES-256-CBC |
| Key Derivation | PBKDF2 |
| Iterations | 100,000 |
| Tool | openssl |
