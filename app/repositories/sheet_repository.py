from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sheet import Sheet


class SheetRepository:
    async def get_all(self, db: AsyncSession) -> list[Sheet]:
        result = await db.execute(select(Sheet))
        return list(result.scalars().all())

    async def get_by_id(self, db: AsyncSession, sheet_id: str) -> Sheet | None:
        return await db.get(Sheet, sheet_id)

    async def save(self, db: AsyncSession, sheet: Sheet) -> None:
        db.add(sheet)
        await db.flush()

    async def update_status(self, db: AsyncSession, sheet_id: str, status: str) -> None:
        sheet = await db.get(Sheet, sheet_id)
        if sheet:
            sheet.status = status
            await db.flush()

    async def filter_by(
        self,
        db: AsyncSession,
        period: str | None = None,
        status: str | None = None,
        position: str | None = None,
    ) -> list[Sheet]:
        query = select(Sheet)
        if period:
            query = query.where(Sheet.period == period)
        if status:
            query = query.where(Sheet.status == status)
        if position:
            query = query.where(Sheet.position == position)
        result = await db.execute(query)
        return list(result.scalars().all())


sheet_repository = SheetRepository()
