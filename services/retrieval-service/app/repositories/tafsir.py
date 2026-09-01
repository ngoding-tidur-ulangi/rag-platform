from sqlalchemy import select, Row
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database.models.tafsir import Tafsir
from typing import Sequence

class TafsirRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_tafsir(
        self, 
        surah_number: int, 
        verse_number: int, 
        commentator: str = "mukhtasar"
    ) -> Row | None:
        query = select(
            Tafsir.commentator,
            Tafsir.text
        ).where(
            Tafsir.surah_number == surah_number,
            Tafsir.verse_number == verse_number,
            Tafsir.commentator == commentator
        )
        result = await self.session.execute(query)
        return result.first()

    async def get_tafsir_range(
        self,
        surah_number: int,
        start_verse: int,
        end_verse: int,
        commentator: str = "mukhtasar"
    ) -> list[Row]:
        query = select(
            Tafsir.commentator,
            Tafsir.text,
            Tafsir.verse_number
        ).where(
            Tafsir.surah_number == surah_number,
            Tafsir.verse_number >= start_verse,
            Tafsir.verse_number <= end_verse,
            Tafsir.commentator == commentator
        )
        result = await self.session.execute(query)
        return list(result.all())

    async def get_tafsirs_for_verses(self, verse_keys: list[tuple[int, int]]) -> list[Row]:
        if not verse_keys:
            return []
        
        from sqlalchemy import tuple_
        query = select(
            Tafsir.surah_number,
            Tafsir.verse_number,
            Tafsir.commentator,
            Tafsir.text
        ).where(
            tuple_(Tafsir.surah_number, Tafsir.verse_number).in_(verse_keys),
            Tafsir.commentator == "mukhtasar"
        )
        
        result = await self.session.execute(query)
        return list(result.all())