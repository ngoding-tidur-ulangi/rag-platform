from pydantic import BaseModel
from typing import List

class AskRequest(BaseModel):
    question: str
    conversation_id: str

class AskResponse(BaseModel):
    answer: str
    context: List[str]
    
class AskStreamResponse(BaseModel):
    status: str | None = None
    answer: str | None = None
    context: List[str] | None = None


class TafsirSchema(BaseModel):
    commentator: str
    text: str
    verse_number: int | None = None

class VerseSchema(BaseModel):
    surah_number: int
    verse_number: int
    surah_name: str
    transliteration: str
    type: str
    verse: str
    translation: str
    hizb: int
    hizb_quarter: int
    page: int
    ruku: int
    manzil: int
    tafsir: TafsirSchema | None = None

class SurahInfoSchema(BaseModel):
    surah_number: int
    surah_name: str
    transliteration: str
    type: str
    verse_count: int