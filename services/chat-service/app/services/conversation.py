import uuid
from datetime import datetime
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.conversation import ConversationRepository
from app.schemas.conversation import ConversationResponse
from shared.database.models.conversation import Conversation
from shared.common.exceptions import NotFoundException

class ConversationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ConversationRepository(session)

    async def get_conversation_list(self, client_id: uuid.UUID) -> List[ConversationResponse]:
        conversations = await self.repository.get_by_client_id(client_id)
        return [ConversationResponse.model_validate(c) for c in conversations]

    async def get_conversation(self, conversation_id: uuid.UUID, client_id: uuid.UUID) -> Conversation:
        conversation = await self.repository.get_by_id(conversation_id)
        if not conversation or conversation.client_id != client_id:
            raise NotFoundException(f"Conversation with id {conversation_id} not found")
        return conversation

    async def create_conversation(self, client_id: uuid.UUID) -> ConversationResponse:
        random_title = f"Conversation-{uuid.uuid4().hex[:8]}"
        conversation = Conversation(
            client_id=client_id,
            title=random_title
        )
        created = await self.repository.create(conversation)
        await self.session.commit()
        return ConversationResponse.model_validate(created)

    async def update_conversation_title(self, conversation_id: uuid.UUID, client_id: uuid.UUID, title: str) -> ConversationResponse:
        conversation = await self.get_conversation(conversation_id, client_id)
        
        conversation.title = title
        updated = await self.repository.update(conversation)
        await self.session.commit()
        return ConversationResponse.model_validate(updated)

    async def delete_conversation(self, conversation_id: uuid.UUID, client_id: uuid.UUID) -> None:
        conversation = await self.get_conversation(conversation_id, client_id)
        await self.repository.delete(conversation)
        await self.session.commit()

    async def update_last_message_at(self, conversation_id: uuid.UUID, last_message_at: datetime) -> ConversationResponse:
        conversation = await self.repository.get_by_id(conversation_id)
        if not conversation:
            raise NotFoundException(f"Conversation with id {conversation_id} not found")
        
        conversation.last_message_at = last_message_at
        updated = await self.repository.update(conversation)
        await self.session.commit()
        return ConversationResponse.model_validate(updated)
