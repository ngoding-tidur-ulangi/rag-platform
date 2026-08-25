# app/schemas/conversation.py
from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict

class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    client_id: uuid.UUID
    title: str
    last_message_at: datetime
    created_at: datetime
    updated_at: datetime
    
class ConversationUpdateTitle(BaseModel):
    title: str

class ConversationUpdateLastMessage(BaseModel):
    last_message_at: datetime
