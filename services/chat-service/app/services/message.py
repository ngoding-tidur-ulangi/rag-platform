import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.message import MessageRepository
from app.repositories.conversation import ConversationRepository
from shared.database.models.message import Message, MessageRole

class MessageService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = MessageRepository(session)
        self.conversation_repository = ConversationRepository(session)

    async def create_message(self, conversation_id: uuid.UUID, content: str, role: str = "USER") -> Message:
        message = Message(
            conversation_id=conversation_id,
            content=content,
            role=MessageRole(role.upper())
        )
        created = await self.repository.create(message)
        
        # Update conversation last_message_at
        conversation = await self.conversation_repository.get_by_id(conversation_id)
        if conversation:
            conversation.last_message_at = created.created_at
            await self.conversation_repository.update(conversation)
            
        await self.session.commit()
        return created
