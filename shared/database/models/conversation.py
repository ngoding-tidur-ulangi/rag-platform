from datetime import datetime
import uuid
from typing import List
from sqlalchemy import func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class Conversation(Base):
    __tablename__ = "conversation"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True,
        default=uuid.uuid4
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("client.id"),
        nullable=False
    )
    title: Mapped[str] = mapped_column(
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), 
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    last_message_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False
    )

    client: Mapped["Client"] = relationship("Client", back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship(
        "Message", 
        back_populates="conversation",
        cascade="all, delete-orphan"
    )
