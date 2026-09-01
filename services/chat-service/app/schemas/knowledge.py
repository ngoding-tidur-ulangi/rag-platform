from datetime import datetime
import uuid
from typing import List
from pydantic import BaseModel, ConfigDict

class KnowledgeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    message_id: uuid.UUID
    function_name: str
    context: List[str]
    created_at: datetime
