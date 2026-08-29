from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from shared.database.models.quran import Quran
from shared.database.models.tafsir import Tafsir
from app.services.llm_service import LLMService
from app.schemas.retrieval import AskResponse

class RetrievalService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm = LLMService()

    async def process_ask(self, question: str) -> AskResponse:
        # 1. Decide retrieval method
        decision = await self.llm.decide_retrieval_method(question)
        
        results = []
        if decision["method"] == "exact" and decision.get("surah_number"):
            results = await self._exact_search(decision["surah_number"], decision.get("verse_number"))
        else:
            results = await self._semantic_search(question)

        # 2. Prepare context
        context_items = []
        context_texts = []
        for q, t in results:
            key = f"{q.surah_number}:{q.verse_number}:{t.commentator if t else 'original'}"
            context_items.append(key)
            text = f"Surah {q.surah_number} Verse {q.verse_number}: {q.verse} - Translation: {q.translation}"
            if t:
                text += f" - Tafsir ({t.commentator}): {t.text}"
            context_texts.append(text)

        context_str = "\n\n".join(context_texts)

        # 3. Generate answer
        answer = await self.llm.generate_answer(question, context_str)

        return AskResponse(answer=answer, context=context_items)

    async def _exact_search(self, surah_number: int, verse_number: int = None):
        stmt = select(Quran, Tafsir).outerjoin(Tafsir, (Quran.surah_number == Tafsir.surah_number) & (Quran.verse_number == Tafsir.verse_number))
        stmt = stmt.where(Quran.surah_number == surah_number)
        if verse_number:
            stmt = stmt.where(Quran.verse_number == verse_number)
        
        result = await self.db.execute(stmt)
        return result.all()

    async def _semantic_search(self, question: str):
        # Basic keyword search as a placeholder for semantic search
        stmt = select(Quran, Tafsir).outerjoin(Tafsir, (Quran.surah_number == Tafsir.surah_number) & (Quran.verse_number == Tafsir.verse_number))
        stmt = stmt.where(
            or_(
                Quran.verse.ilike(f"%{question}%"),
                Quran.translation.ilike(f"%{question}%")
            )
        ).limit(5)
        
        result = await self.db.execute(stmt)
        return result.all()
