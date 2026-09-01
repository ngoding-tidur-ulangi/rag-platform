import logging

import json
from pyexpat.errors import messages
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from app.services.llm_service import LLMService
from typing import AsyncGenerator
from app.schemas.retrieval import AskResponse, AskStreamResponse, SurahInfoSchema, TafsirSchema, VerseSchema
from app.repositories.quran import QuranRepository
from app.repositories.tafsir import TafsirRepository
from app.repositories.knowledge import KnowledgeRepository
from app.repositories.message import MessageRepository

logger = logging.getLogger(__name__)

from app.prompts.loader import ANSWER_GENERATION_PROMPT, QUESTION_ROUTER_PROMPT


from shared.database.models.message import Message, MessageRole
from shared.database.models.knowledge import Knowledge

class RetrievalService:
    def __init__(self, session: AsyncSession, llm: LLMService):
        self.session = session
        self.quran_repository = QuranRepository(session)
        self.tafsir_repository = TafsirRepository(session)
        self.message_repository = MessageRepository(session)
        self.knowledge_repository = KnowledgeRepository(session)
        self.llm = llm

    async def process_ask(self, conversation_id: uuid.UUID, question: str) -> AsyncGenerator[AskStreamResponse, None]:
        logger.info(f"Processing ask for conversation {conversation_id}: {question[:50]}...")
        yield AskStreamResponse(status="Analyzing")
        
        messages = await self.message_repository.get_by_conversation_id(conversation_id)
        logger.info(f"Retrieved {len(messages)} history messages")
        history_context = []
        for msg in messages:
            history_context.append(f"{msg.role.value}: {msg.content}")
            
            knowledges = await self.knowledge_repository.get_by_message_id(msg.id)
            for k in knowledges:
                history_context.append(f"Context used for above: {'; '.join(k.context)}")

        history_str = "\n".join(history_context)
        full_query = f"HISTORY\n{history_str}\nUSER: {question}" if history_str else question

        logger.info("Calling LLM for routing decision...")
        result = await self.llm.llm_call(full_query, QUESTION_ROUTER_PROMPT)
        try:
            decision = json.loads(result)
            function_name = decision.get("function")
            arguments = decision.get("arguments", {})
            logger.info(f"Router decision: {function_name} with args: {arguments}")
        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM router decision: {result}")
            function_name = None
            arguments = {}

        yield AskStreamResponse(status="Retrieving data")

        if function_name in self.FUNCTIONS:
            logger.info(f"Executing function: {function_name}")
            results = await self.FUNCTIONS[function_name](self, **arguments)
            logger.info(f"Function {function_name} returned {results}")
            if not isinstance(results, list): results = [results] if results else []
        else:
            logger.info(f"Fallback to vector search (function_name: {function_name})")
            results = await self._search_quran(full_query)
        
        logger.info(f"Retrieved {len(results)} context results")
        context_items, context_texts = [], []
        for item in results:
            if isinstance(item, VerseSchema):
                commentator = item.tafsir.commentator if item.tafsir else "mukhtasar"
                key = f"{item.surah_number}:{item.verse_number}:{commentator}"
                text = f"Surah {item.surah_number} Verse {item.verse_number}: {item.verse} ({item.translation})"
                if item.tafsir: text += f" | Tafsir: {item.tafsir.text}"
            elif isinstance(item, SurahInfoSchema):
                key = f"surah:{item.surah_number}"
                text = f"Surah {item.surah_number} ({item.surah_name}): {item.verse_count} verses, {item.type}"
            else: continue
            
            context_items.append(key)
            context_texts.append(text)

        yield AskStreamResponse(status="Building final response", context=context_items)

        full_query = f"HISTORY\n{history_str}\nCONTEXT\n{('\n'.join(context_texts))}\nUSER: {question}"
        
        logger.info("Starting final response stream...")
        full_answer = ""
        async for chunk in self.llm.llm_stream(full_query, ANSWER_GENERATION_PROMPT):
            full_answer += chunk
            yield AskStreamResponse(answer=chunk)
        
        logger.info(f"Finished processing ask for conversation {conversation_id}")

        # Save assistant message and knowledge context
        if full_answer:
            assistant_msg = Message(
                conversation_id=conversation_id,
                content=full_answer,
                role=MessageRole.SYSTEM
            )
            created_msg = await self.message_repository.create(assistant_msg)
            
            knowledge = Knowledge(
                message_id=created_msg.id,
                function_name=function_name or "search_quran",
                context=context_items
            )
            await self.knowledge_repository.create(knowledge)
            await self.session.commit()
            logger.info(f"Saved assistant message and knowledge for message {created_msg.id}")

    async def _get_verse(self, surah_number: int, verse_number: int) -> VerseSchema | None:
        verse = await self.quran_repository.get_verse(surah_number, verse_number)
        if not verse:
            return None
        tafsir = await self.tafsir_repository.get_tafsir(surah_number, verse_number)

        return VerseSchema(
            **verse._mapping,
            tafsir=TafsirSchema(**tafsir._mapping) if tafsir else None
        )

    async def _get_verse_range(self, surah_number: int, start_verse: int, end_verse: int) -> list[VerseSchema]:
        verses = await self.quran_repository.get_verse_range(surah_number, start_verse, end_verse)
        tafsirs = await self.tafsir_repository.get_tafsir_range(surah_number, start_verse, end_verse)
        tafsir_map = {t.verse_number: t for t in tafsirs}

        results = []
        for v in verses:
            t_row = tafsir_map.get(v.verse_number)
            results.append(VerseSchema(
                **v._mapping,
                tafsir=TafsirSchema(**t_row._mapping) if t_row else None
            ))
        return results

    async def _search_quran(self, query: str):
        payloads = await self.llm.vector_search(query)
        keys = []
        for p in payloads:
            if "id" in p:
                try:
                    parts = p["id"].split(":")
                    if len(parts) >= 2:
                        keys.append((int(parts[0]), int(parts[1])))
                except (ValueError, IndexError):
                    logger.warning(f"Failed to parse payload id: {p.get('id')}")
            elif "surah_number" in p and "verse_number" in p:
                keys.append((int(p["surah_number"]), int(p["verse_number"])))

        if not keys: return []

        verse_rows = await self.quran_repository.get_verses_by_keys(keys)
        tafsir_rows = await self.tafsir_repository.get_tafsirs_for_verses(keys)
        tafsir_map = {(t.surah_number, t.verse_number): t for t in tafsir_rows}

        return [VerseSchema(
            **v._mapping, 
            tafsir=TafsirSchema(**tafsir_map[(v.surah_number, v.verse_number)]._mapping) 
            if (v.surah_number, v.verse_number) in tafsir_map else None
        ) for v in verse_rows]

    async def _find_keyword(self, keyword: str) -> list[VerseSchema]:
        verse_rows = await self.quran_repository.search_by_keyword(keyword)
        if not verse_rows:
            return []
        verse_keys = [(v.surah_number, v.verse_number) for v in verse_rows]
        tafsir_rows = await self.tafsir_repository.get_tafsirs_for_verses(verse_keys)
        tafsir_map = {(t.surah_number, t.verse_number): t for t in tafsir_rows}

        results = []
        for v in verse_rows:
            t_data = tafsir_map.get((v.surah_number, v.verse_number))
            results.append(VerseSchema(
                **v._mapping,
                tafsir=TafsirSchema(**t_data._mapping) if t_data else None
            ))
        
        return results

    async def _get_surah_info(self, surah_number: int) -> SurahInfoSchema | None:
        row = await self.quran_repository.get_surah_info(surah_number)
        if not row:
            return None
        return SurahInfoSchema(**row._mapping)

    async def _find_verses_by_metadata(self, **kwargs) -> list[VerseSchema]:
        verse_rows = await self.quran_repository.get_verses_by_metadata(**kwargs)
        if not verse_rows:
            return []
        
        verse_keys = [(v.surah_number, v.verse_number) for v in verse_rows]
        tafsir_rows = await self.tafsir_repository.get_tafsirs_for_verses(verse_keys)
        tafsir_map = {(t.surah_number, t.verse_number): t for t in tafsir_rows}

        return [
            VerseSchema(
                **v._mapping,
                tafsir=TafsirSchema(**tafsir_map[(v.surah_number, v.verse_number)]._mapping) 
                if (v.surah_number, v.verse_number) in tafsir_map else None
            ) for v in verse_rows
        ]

    FUNCTIONS = {
        "get_verse": _get_verse,
        "get_verse_range": _get_verse_range,
        "search_quran": _search_quran,
        "find_keyword": _find_keyword,
        "get_surah_info": _get_surah_info,
        "find_verses_by_metadata": _find_verses_by_metadata,
    }