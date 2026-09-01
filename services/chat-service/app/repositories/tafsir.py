from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database.models.tafsir import Tafsir

class TafsirRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_verse(self, surah_number: int, verse_number: int, commentator: Optional[str] = None) -> list[Tafsir]:
        query = (
            select(Tafsir)
            .where(
                Tafsir.surah_number == surah_number,
                Tafsir.verse_number == verse_number
            )
        )
        if commentator:
            query = query.where(Tafsir.commentator == commentator)
            
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_specific_tafsir(self, surah_number: int, verse_number: int, commentator: str) -> Optional[Tafsir]:
        query = (
            select(Tafsir)
            .where(
                Tafsir.surah_number == surah_number,
                Tafsir.verse_number == verse_number,
                Tafsir.commentator == commentator
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
