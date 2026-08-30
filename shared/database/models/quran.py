from typing import List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import TSVECTOR
from shared.database.models.base import Base
from sqlalchemy import Index

if TYPE_CHECKING:
    from shared.database.models.tafsir import Tafsir

class Quran(Base):
    __tablename__ = "quran"

    __table_args__ = (
        Index(
            "idx_quran_translation_search",
            "translation_search",
            postgresql_using="gin",
        ),
    )

    surah_number: Mapped[int] = mapped_column(primary_key=True)
    verse_number: Mapped[int] = mapped_column(primary_key=True)
    surah_name: Mapped[str] = mapped_column()
    transliteration: Mapped[str] = mapped_column()
    type: Mapped[str] = mapped_column()
    verse: Mapped[str] = mapped_column()
    translation: Mapped[str] = mapped_column()
    hizb: Mapped[int] = mapped_column()
    hizb_quarter: Mapped[int] = mapped_column()
    page: Mapped[int] = mapped_column()
    ruku: Mapped[int] = mapped_column()
    manzil: Mapped[int] = mapped_column()
    translation_search: Mapped[str] = mapped_column(TSVECTOR, nullable=True)

    tafsirs: Mapped[List["Tafsir"]] = relationship(
        "Tafsir", 
        back_populates="quran",
        cascade="all, delete-orphan"
    )
