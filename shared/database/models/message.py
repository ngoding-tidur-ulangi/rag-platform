import enum
from datetime import datetime
import uuid
from sqlalchemy import ForeignKey, func, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class MessageRole(str, enum.Enum):
    SYSTEM = "SYSTEM"
    USER = "USER"

class Message(Base):
    __tablename__ = "message"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True,
        default=uuid.uuid4
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("conversation.id"),
        nullable=False
    )
    role: Mapped[MessageRole] = mapped_column(
        Enum(MessageRole, name="messagerole"),
        nullable=False
    )
    content: Mapped[str] = mapped_column(
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), 
        nullable=False
    )

    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")
