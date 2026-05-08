from pydantic import BaseModel


class SheetCreatedItem(BaseModel):
    sheet_id: str
    employee_id: str
    google_sheet_url: str
    status: str


class GenerateResponse(BaseModel):
    status: str
    sheets_created: int
    sheets: list[SheetCreatedItem]


class SheetListResponse(BaseModel):
    sheets: list[dict]
    total: int


class ValidationResult(BaseModel):
    sheet_id: str
    status: str
    errors: list[dict]
    warnings: list[dict]


class BatchValidateResponse(BaseModel):
    results: list[ValidationResult]


class MigratedItem(BaseModel):
    sheet_id: str
    employee_id: str
    old_grade: str
    new_grade: str


class MigrateResponse(BaseModel):
    status: str
    migrated: int
    sheets: list[MigratedItem]
