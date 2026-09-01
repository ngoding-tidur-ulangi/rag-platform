from typing import TYPE_CHECKING
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shared.database.models.base import Base

if TYPE_CHECKING:
    from shared.database.models.quran import Quran

class Tafsir(Base):
    __tablename__ = "tafsir"

    surah_number: Mapped[int] = mapped_column(primary_key=True)
    verse_number: Mapped[int] = mapped_column(primary_key=True)
    commentator: Mapped[str] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column()

    quran: Mapped["Quran"] = relationship("Quran", back_populates="tafsirs")

    __table_args__ = (
        ForeignKeyConstraint(
            ["surah_number", "verse_number"],
            ["quran.surah_number", "quran.verse_number"],
        ),
    )
