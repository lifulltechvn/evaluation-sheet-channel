# Evaluation Sheet API

Backend API phục vụ hệ thống quản lý phiếu đánh giá nhân viên, xây dựng theo mô hình **BFF (Backend For Frontend)** với FastAPI.

## Mục lục

- [Kiến trúc tổng quan](#kiến-trúc-tổng-quan)
- [Cấu trúc thư mục](#cấu-trúc-thư-mục)
- [Giải thích từng layer](#giải-thích-từng-layer)
- [Luồng xử lý request](#luồng-xử-lý-request)
- [Cài đặt và chạy](#cài-đặt-và-chạy)
- [API Endpoints](#api-endpoints)
- [Cấu hình Database (PostgreSQL)](#cấu-hình-database-postgresql)
- [Database Migration (Alembic)](#database-migration-alembic)
- [Hướng dẫn phát triển](#hướng-dẫn-phát-triển)

---

## Kiến trúc tổng quan

Dự án áp dụng kiến trúc **Layered Architecture** kết hợp mô hình BFF:

```
Frontend (Web/Mobile)
        │
        ▼
┌─────────────────┐
│   Router (BFF)  │  ← Nhận HTTP request, validate input, trả response
├─────────────────┤
│    Service       │  ← Business logic, orchestration
├─────────────────┤
│   Repository     │  ← Truy cập dữ liệu (DB, external API)
├─────────────────┤
│   Models/Data    │  ← Data store, DB models
└─────────────────┘
```

**Nguyên tắc thiết kế:**

- Mỗi layer chỉ gọi layer ngay bên dưới, không bỏ qua layer
- Router không chứa business logic
- Service không biết HTTP (không import FastAPI)
- Repository không chứa logic nghiệp vụ

---

## Cấu trúc thư mục

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Entry point — khởi tạo FastAPI app, mount routers
│   ├── config.py               # Cấu hình ứng dụng (CORS, DB, đọc từ .env)
│   │
│   ├── routers/                # 🔵 BFF Layer — định nghĩa API endpoints
│   │   ├── sheet_router.py         # /v1/sheets/*
│   │   ├── employee_router.py      # /v1/employees/*
│   │   ├── notification_router.py  # /v1/notifications/*
│   │   └── dashboard_router.py     # /v1/dashboard/*
│   │
│   ├── schemas/                # 🟡 Request/Response models (Pydantic)
│   │   ├── sheet_schema.py
│   │   ├── employee_schema.py
│   │   ├── notification_schema.py
│   │   └── dashboard_schema.py
│   │
│   ├── services/               # 🟢 Business logic
│   │   ├── sheet_service.py        # Logic CRUD, validate, migrate sheets
│   │   ├── employee_service.py     # Logic quản lý nhân viên
│   │   ├── notification_service.py # Logic gửi thông báo
│   │   └── scoring_service.py      # Logic tính điểm theo position/grade
│   │
│   ├── repositories/           # 🟠 Data access layer
│   │   ├── sheet_repository.py     # Đọc/ghi dữ liệu sheets
│   │   └── employee_repository.py  # Đọc/ghi dữ liệu nhân viên
│   │
│   ├── models/                 # 🔴 Database models (SQLAlchemy) + Mock data
│   │   ├── employee.py             # Model bảng employees
│   │   ├── sheet.py                # Model bảng sheets
│   │   ├── history.py              # Model bảng evaluation_history
│   │   └── mock_data.py            # Mock database (dict in-memory)
│   │
│   └── common/                 # ⚪ Shared utilities
│       ├── database.py             # SQLAlchemy engine, session, get_db()
│       ├── exceptions.py           # Custom exceptions (NotFoundException...)
│       └── middleware.py           # CORS và các middleware khác
│
├── alembic/                    # 🟣 Database migrations
│   ├── env.py                      # Alembic config (tự đọc từ app settings)
│   ├── script.py.mako              # Template tạo migration file
│   └── versions/                   # Các file migration
│
├── .env                        # Biến môi trường (DB config) — KHÔNG commit
├── .env.example                # Template .env cho developer mới
├── .gitignore
├── alembic.ini                 # Alembic settings
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Giải thích từng layer

### `routers/` — BFF Layer

Đây là **điểm tiếp xúc duy nhất** giữa frontend và backend. Mỗi file router tương ứng với một nhóm API.

**Trách nhiệm:**
- Định nghĩa HTTP endpoints (GET, POST, PUT, DELETE)
- Validate request input thông qua Pydantic schemas
- Gọi service tương ứng để xử lý
- Format và trả response cho frontend

**Không được làm:**
- Chứa business logic
- Truy cập trực tiếp database/repository

```python
# Ví dụ: app/routers/sheet_router.py
@router.post("/generate")
def generate_sheets(req: GenerateRequest):
    employees = [emp.model_dump() for emp in req.employees]
    return sheet_service.generate(req.period, employees)  # Gọi service
```

### `schemas/` — Request/Response Models

Định nghĩa cấu trúc dữ liệu đầu vào (request) và đầu ra (response) bằng **Pydantic BaseModel**.

**Trách nhiệm:**
- Validate dữ liệu tự động (type, required fields...)
- Tạo documentation tự động trên Swagger UI
- Tách biệt data contract giữa frontend và backend

```python
# Ví dụ: app/schemas/sheet_schema.py
class GenerateRequest(BaseModel):
    period: str
    employees: list[EmployeeInput]
```

### `services/` — Business Logic

Chứa **toàn bộ logic nghiệp vụ**. Đây là nơi quan trọng nhất của ứng dụng.

**Trách nhiệm:**
- Xử lý logic nghiệp vụ (generate sheet, validate, migrate...)
- Orchestrate nhiều repository nếu cần
- Throw exception khi có lỗi nghiệp vụ

**Không được làm:**
- Import FastAPI (không biết HTTP)
- Truy cập trực tiếp data store

```python
# Ví dụ: app/services/sheet_service.py
class SheetService:
    def generate(self, period, employees):
        # Business logic ở đây
        scoring = scoring_service.get_scoring(emp["position"], emp["grade"])
        sheet_repository.save(sheet_id, sheet)
```

### `repositories/` — Data Access Layer

Chịu trách nhiệm **đọc/ghi dữ liệu**. Hiện tại dùng mock data (dict in-memory), sau này đổi sang database thật chỉ cần sửa layer này.

**Trách nhiệm:**
- CRUD operations trên data store
- Query, filter dữ liệu
- Là layer duy nhất được truy cập trực tiếp vào models/data

```python
# Ví dụ: app/repositories/sheet_repository.py
class SheetRepository:
    def get_by_id(self, sheet_id: str) -> dict | None:
        return SHEETS_DB.get(sheet_id)
```

### `models/` — Database Models & Data Store

Chứa **SQLAlchemy ORM models** ánh xạ tới các bảng trong PostgreSQL, và mock data cho development.

| File | Bảng DB | Mô tả |
|------|---------|--------|
| `employee.py` | `employees` | Thông tin nhân viên |
| `sheet.py` | `sheets` | Phiếu đánh giá |
| `history.py` | `evaluation_history` | Lịch sử đánh giá |
| `mock_data.py` | — | Dữ liệu giả cho development |

```python
# Ví dụ: app/models/employee.py
class Employee(Base):
    __tablename__ = "employees"
    employee_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
```

### `common/` — Shared Utilities

Chứa các thành phần dùng chung:

| File | Mô tả |
|------|--------|
| `database.py` | SQLAlchemy async engine, session factory, `get_db()` dependency |
| `exceptions.py` | Custom exceptions (`NotFoundException`, `BadRequestException`) |
| `middleware.py` | CORS config và các middleware khác |

---

## Luồng xử lý request

Ví dụ khi frontend gọi `POST /v1/sheets/generate`:

```
1. Frontend gửi POST request
        │
2. sheet_router.py nhận request
   → Validate input bằng GenerateRequest schema
        │
3. Gọi sheet_service.generate()
   → Tính scoring qua scoring_service
   → Tạo sheet object
        │
4. Gọi sheet_repository.save()
   → Lưu vào SHEETS_DB (mock data)
        │
5. Router trả response JSON cho frontend
```

---

## Cài đặt và chạy

### Yêu cầu

- Python 3.12 hoặc 3.13
- PostgreSQL 14+ (local hoặc Docker)

### Bước 1: Tạo virtual environment và cài dependencies

```bash
# Tạo virtual environment (dùng Python 3.13 nếu có)
python3.13 -m venv venv
source venv/bin/activate

# Cài dependencies
pip install -r requirements.txt
```

### Bước 2: Cấu hình môi trường

```bash
# Copy file env mẫu
cp .env.example .env
```

Mở `.env` và chỉnh sửa nếu cần:

```env
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_NAME=evaluation_sheet
```

### Bước 3: Tạo database PostgreSQL

```bash
# Tạo database (dùng user postgres mặc định)
createdb evaluation_sheet

# Hoặc nếu cần chỉ định user
createdb -U postgres evaluation_sheet
```

Nếu dùng **pgAdmin** hoặc **DBeaver**, tạo database mới tên `evaluation_sheet`.

### Bước 4: Chạy database migration

```bash
# Tạo migration đầu tiên từ models
alembic revision --autogenerate -m "create initial tables"

# Áp dụng migration vào database
alembic upgrade head
```

### Bước 5: Chạy server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Chạy bằng Docker

```bash
docker build -t evaluation-sheet-api .
docker run -p 8000:8000 evaluation-sheet-api
```

### Truy cập

| URL | Mô tả |
|-----|--------|
| http://localhost:8000 | Root endpoint |
| http://localhost:8000/docs | Swagger UI (API documentation) |
| http://localhost:8000/v1/health | Health check |

---

## API Endpoints

### Sheets
| Method | Endpoint | Mô tả |
|--------|----------|--------|
| POST | `/v1/sheets/generate` | Tạo phiếu đánh giá cho nhân viên |
| GET | `/v1/sheets` | Danh sách phiếu (filter: period, status, position) |
| GET | `/v1/sheets/{sheet_id}` | Chi tiết một phiếu |
| POST | `/v1/sheets/{sheet_id}/send` | Gửi phiếu qua email |
| POST | `/v1/sheets/batch-send` | Gửi nhiều phiếu cùng lúc |
| POST | `/v1/sheets/{sheet_id}/validate` | Validate phiếu (AI mock) |
| POST | `/v1/sheets/batch-validate` | Validate nhiều phiếu |
| POST | `/v1/sheets/migrate` | Migrate phiếu sang kỳ mới |

### Employees
| Method | Endpoint | Mô tả |
|--------|----------|--------|
| GET | `/v1/employees` | Danh sách nhân viên |
| GET | `/v1/employees/{id}/history` | Lịch sử đánh giá |

### Notifications
| Method | Endpoint | Mô tả |
|--------|----------|--------|
| POST | `/v1/notifications/send-results` | Gửi kết quả đánh giá |

### Dashboard
| Method | Endpoint | Mô tả |
|--------|----------|--------|
| GET | `/v1/dashboard/status` | Thống kê tổng quan |

---

## Cấu hình Database (PostgreSQL)

### Cấu trúc kết nối

```
app/config.py          ← Đọc biến môi trường từ .env
        │
app/common/database.py ← Tạo SQLAlchemy engine + session
        │
app/models/*.py        ← Định nghĩa bảng (ORM models)
        │
app/repositories/*.py  ← Sử dụng session để query
```

### File `.env`

Tất cả config database nằm trong file `.env` ở root project:

```env
DATABASE_HOST=localhost      # Host PostgreSQL
DATABASE_PORT=5432           # Port (mặc định 5432)
DATABASE_USER=postgres       # Username
DATABASE_PASSWORD=postgres   # Password
DATABASE_NAME=evaluation_sheet  # Tên database
```

File `.env` **không được commit** lên git (đã có trong `.gitignore`). Developer mới copy từ `.env.example`.

### Cách config hoạt động

`app/config.py` dùng `pydantic-settings` để tự động đọc `.env`:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_host: str = "localhost"
    database_port: int = 5432
    database_user: str = "postgres"
    database_password: str = "postgres"
    database_name: str = "evaluation_sheet"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )

    model_config = {"env_file": ".env"}
```

Biến `DATABASE_HOST` trong `.env` tự động map vào `settings.database_host`.

### Database Session (Dependency Injection)

`app/common/database.py` cung cấp `get_db()` — dùng làm dependency trong router:

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.common.database import get_db

@router.get("/items")
async def list_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item))
    return result.scalars().all()
```

Mỗi request sẽ nhận một session riêng, tự động commit khi thành công và rollback khi có lỗi.

### Các bảng trong database

| Bảng | Model | Mô tả |
|------|-------|--------|
| `employees` | `app/models/employee.py` | Thông tin nhân viên (id, name, email, position, grade) |
| `sheets` | `app/models/sheet.py` | Phiếu đánh giá (scoring criteria, status, period...) |
| `evaluation_history` | `app/models/history.py` | Lịch sử đánh giá qua các kỳ |

---

## Database Migration (Alembic)

Alembic quản lý việc thay đổi cấu trúc database (thêm bảng, thêm cột, đổi kiểu dữ liệu...) một cách có kiểm soát.

### Các lệnh thường dùng

```bash
# Tạo migration mới từ thay đổi trong models
alembic revision --autogenerate -m "mô tả thay đổi"

# Áp dụng tất cả migration chưa chạy
alembic upgrade head

# Rollback 1 migration
alembic downgrade -1

# Xem migration hiện tại
alembic current

# Xem lịch sử migration
alembic history
```

### Quy trình khi thay đổi database

**Ví dụ: Thêm cột `phone` vào bảng `employees`**

**Bước 1:** Sửa model

```python
# app/models/employee.py
class Employee(Base):
    __tablename__ = "employees"
    # ... các cột cũ ...
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)  # MỚI
```

**Bước 2:** Tạo migration

```bash
alembic revision --autogenerate -m "add phone column to employees"
```

Alembic sẽ tự detect thay đổi và tạo file migration trong `alembic/versions/`.

**Bước 3:** Kiểm tra file migration vừa tạo

Mở file trong `alembic/versions/` và review hàm `upgrade()` / `downgrade()`.

**Bước 4:** Áp dụng

```bash
alembic upgrade head
```

### Lưu ý quan trọng

- **Luôn review** file migration trước khi chạy `upgrade`
- **Không sửa** file migration đã được chạy trên môi trường khác
- **Commit** file migration lên git để team đồng bộ
- Alembic tự đọc `DATABASE_URL` từ `app/config.py`, không cần sửa `alembic.ini`

---

## Hướng dẫn phát triển

### Thêm một endpoint mới

Ví dụ: thêm API xóa sheet `DELETE /v1/sheets/{sheet_id}`

**Bước 1:** Thêm method vào repository (nếu cần)
```python
# app/repositories/sheet_repository.py
def delete(self, sheet_id: str) -> bool:
    if sheet_id in SHEETS_DB:
        del SHEETS_DB[sheet_id]
        return True
    return False
```

**Bước 2:** Thêm business logic vào service
```python
# app/services/sheet_service.py
def delete_sheet(self, sheet_id: str) -> dict:
    sheet = self.get_sheet(sheet_id)  # Raise 404 nếu không tìm thấy
    sheet_repository.delete(sheet_id)
    return {"status": "success", "deleted": sheet_id}
```

**Bước 3:** Thêm endpoint vào router
```python
# app/routers/sheet_router.py
@router.delete("/{sheet_id}")
def delete_sheet(sheet_id: str):
    return sheet_service.delete_sheet(sheet_id)
```

### Thêm một domain mới

Ví dụ: thêm module **Reports**

1. Tạo `app/schemas/report_schema.py`
2. Tạo `app/repositories/report_repository.py`
3. Tạo `app/services/report_service.py`
4. Tạo `app/routers/report_router.py`
5. Mount router trong `app/main.py`:
   ```python
   from app.routers import report_router
   app.include_router(report_router.router)
   ```

### Đổi repository sang dùng PostgreSQL

Hiện tại repository đang dùng mock data (dict). Để chuyển sang PostgreSQL:

**Bước 1:** Thêm `db: AsyncSession` parameter vào repository

```python
# app/repositories/sheet_repository.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sheet import Sheet

class SheetRepository:
    async def get_by_id(self, db: AsyncSession, sheet_id: str) -> Sheet | None:
        result = await db.execute(select(Sheet).where(Sheet.sheet_id == sheet_id))
        return result.scalar_one_or_none()

    async def save(self, db: AsyncSession, sheet: Sheet) -> None:
        db.add(sheet)
        await db.flush()
```

**Bước 2:** Cập nhật service để truyền `db` session

```python
# app/services/sheet_service.py
class SheetService:
    async def get_sheet(self, db: AsyncSession, sheet_id: str) -> Sheet:
        sheet = await sheet_repository.get_by_id(db, sheet_id)
        if not sheet:
            raise NotFoundException("Sheet not found")
        return sheet
```

**Bước 3:** Cập nhật router để inject `db` dependency

```python
# app/routers/sheet_router.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.common.database import get_db

@router.get("/{sheet_id}")
async def get_sheet(sheet_id: str, db: AsyncSession = Depends(get_db)):
    return await sheet_service.get_sheet(db, sheet_id)
```

Router và service **không thay đổi logic**, chỉ thêm `db` parameter và chuyển sang `async/await`.
