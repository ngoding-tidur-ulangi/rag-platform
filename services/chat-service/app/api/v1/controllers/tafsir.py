from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.services.tafsir import TafsirService
from app.schemas.tafsir import TafsirResponse
from shared.common.schemas import DefaultResponse

router = APIRouter()

@router.get("/tafsir", response_model=DefaultResponse[TafsirResponse])
async def get_tafsir_detail(
    surah_number: int = Query(..., description="Surah number"),
    verse_number: int = Query(..., description="Verse number"),
    commentator: str = Query("mukhtasar", description="Commentator name"),
    db: AsyncSession = Depends(get_db)
):
    service = TafsirService(db)
    res = await service.get_tafsir_detail(surah_number, verse_number, commentator)
    return DefaultResponse.success(data=res)
