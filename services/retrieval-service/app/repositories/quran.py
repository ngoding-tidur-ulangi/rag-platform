from sqlalchemy import func, select, Row
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database.models.quran import Quran
from typing import Sequence



class QuranRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_verse(self, surah_number: int, verse_number: int) -> Row | None:
        query = select(
            Quran.surah_number,
            Quran.verse_number,
            Quran.surah_name,
            Quran.transliteration,
            Quran.type,
            Quran.verse,
            Quran.translation,
            Quran.hizb,
            Quran.hizb_quarter,
            Quran.page,
            Quran.ruku,
            Quran.manzil
        ).where(
            Quran.surah_number == surah_number,
            Quran.verse_number == verse_number
        )
        result = await self.session.execute(query)
        return result.first()

    async def get_verse_range(self, surah_number: int, start_verse: int, end_verse: int) -> list[Row]:
        query = select(
            Quran.surah_number,
            Quran.verse_number,
            Quran.surah_name,
            Quran.transliteration,
            Quran.type,
            Quran.verse,
            Quran.translation,
            Quran.hizb,
            Quran.hizb_quarter,
            Quran.page,
            Quran.ruku,
            Quran.manzil
        ).where(
            Quran.surah_number == surah_number,
            Quran.verse_number >= start_verse,
            Quran.verse_number <= end_verse
        ).order_by(Quran.verse_number.asc())
        
        result = await self.session.execute(query)
        return list(result.all())

    async def search_by_keyword(self, keyword: str) -> list[Row]:
        query = select(
            Quran.surah_number,
            Quran.verse_number,
            Quran.surah_name,
            Quran.transliteration,
            Quran.type,
            Quran.verse,
            Quran.translation,
            Quran.hizb,
            Quran.hizb_quarter,
            Quran.page,
            Quran.ruku,
            Quran.manzil
        ).where(
            Quran.translation_search.bool_op("@@")(func.plainto_tsquery('english', keyword))
        ).limit(10)
        
        result = await self.session.execute(query)
        return list(result.all())

    async def get_surah_info(self, surah_number: int) -> Row | None:
        query = select(
            Quran.surah_number,
            Quran.surah_name,
            Quran.transliteration,
            Quran.type,
            func.count(Quran.verse_number).label("verse_count")
        ).where(
            Quran.surah_number == surah_number
        ).group_by(
            Quran.surah_number,
            Quran.surah_name,
            Quran.transliteration,
            Quran.type
        )
        
        result = await self.session.execute(query)
        return result.first()

    async def get_verses_by_metadata(self, **filters) -> list[Row]:
        query = select(
            Quran.surah_number, Quran.verse_number, Quran.surah_name,
            Quran.transliteration, Quran.type, Quran.verse, Quran.translation,
            Quran.hizb, Quran.hizb_quarter, Quran.page, Quran.ruku, Quran.manzil
        )
        
        for key, value in filters.items():
            if value is not None and hasattr(Quran, key):
                query = query.where(getattr(Quran, key) == value)
        
        query = query.order_by(Quran.surah_number.asc(), Quran.verse_number.asc()).limit(20)
        result = await self.session.execute(query)
        return list(result.all())

    async def get_verses_by_keys(self, keys: list[tuple[int, int]]) -> list[Row]:
        if not keys:
            return []
        
        # Build conditions for multiple (surah, verse) pairs
        conditions = [
            (Quran.surah_number == s) & (Quran.verse_number == v)
            for s, v in keys
        ]
        from sqlalchemy import or_
        query = select(
            Quran.surah_number, Quran.verse_number, Quran.surah_name,
            Quran.transliteration, Quran.type, Quran.verse, Quran.translation,
            Quran.hizb, Quran.hizb_quarter, Quran.page, Quran.ruku, Quran.manzil
        ).where(or_(*conditions))
        
        result = await self.session.execute(query)
        # Order by the original order of keys if possible, or just return
        return list(result.all())
