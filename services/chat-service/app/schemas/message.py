from datetime import datetime
import uuid
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.knowledge import KnowledgeResponse

class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    content: str
    role: str
    created_at: datetime
    knowledge_contexts: List[KnowledgeResponse] = []

class MessageCreate(BaseModel):
    content: str
