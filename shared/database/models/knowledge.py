import uuid
from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import ForeignKey, func, String
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shared.database.models.base import Base

if TYPE_CHECKING:
    from shared.database.models.message import Message

class Knowledge(Base):
    __tablename__ = "knowledge"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True,
        default=uuid.uuid4
    )
    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("message.id"),
        nullable=False
    )
    function_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    context: Mapped[List[str]] = mapped_column(
        ARRAY(String),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), 
        nullable=False
    )

    message: Mapped["Message"] = relationship("Message", back_populates="knowledge_contexts")
