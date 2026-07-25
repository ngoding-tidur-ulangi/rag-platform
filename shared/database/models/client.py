from datetime import datetime
import uuid
from typing import List
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class Client(Base):
    __tablename__ = "client"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), 
        nullable=False
    )
    last_seen: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False
    )

    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation", 
        back_populates="client",
        cascade="all, delete-orphan"
    )
