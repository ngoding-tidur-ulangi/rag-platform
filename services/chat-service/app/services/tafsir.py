import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.tafsir import TafsirRepository
from app.schemas.tafsir import TafsirResponse
from shared.common.exceptions import ApplicationException

logger = logging.getLogger(__name__)

class TafsirService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = TafsirRepository(session)

    async def get_tafsir_detail(self, surah_number: int, verse_number: int, commentator: str = "mukhtasar") -> TafsirResponse:
        logger.info(f"Getting tafsir detail for Surah {surah_number}, Verse {verse_number}, Commentator: {commentator}")
        
        tafsir = await self.repository.get_specific_tafsir(surah_number, verse_number, commentator)
        
        if not tafsir:
            # If default not found, try to find any available tafsir for this verse
            available = await self.repository.get_by_verse(surah_number, verse_number)
            if not available:
                raise ApplicationException(f"Tafsir for Surah {surah_number}, Verse {verse_number} not found", status_code=404)
            
            tafsir = available[0]
            logger.info(f"Requested tafsir not found, falling back to: {tafsir.commentator}")

        return TafsirResponse.model_validate(tafsir)
