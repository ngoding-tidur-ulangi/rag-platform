from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict

class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    content: str
    role: str
    created_at: datetime

class MessageCreate(BaseModel):
    content: str
