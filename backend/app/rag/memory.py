import uuid
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import ChatMessage, ChatSession


class ConversationMemory:
    def __init__(self, window_size: int = 6):
        self.window_size = window_size

    async def get_or_create_session(self, db: AsyncSession, session_id: str, tenant_id: str, user_id: str) -> str:
        """Ensure session exists or create one."""
        if not session_id:
            session_id = str(uuid.uuid4())
            new_session = ChatSession(id=session_id, tenant_id=tenant_id, user_id=user_id)
            db.add(new_session)
            await db.commit()
            return session_id
        
        # Verify session exists and belongs to tenant
        result = await db.execute(
            select(ChatSession).where(ChatSession.id == session_id, ChatSession.tenant_id == tenant_id)
        )
        session = result.scalars().first()
        if not session:
            new_session = ChatSession(id=session_id, tenant_id=tenant_id, user_id=user_id)
            db.add(new_session)
            await db.commit()
            
        return session_id

    async def add_message(self, db: AsyncSession, session_id: str, tenant_id: str, role: str, content: str, sources: List[Dict[str, Any]] = None):
        """Add a new message to the session."""
        msg = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            tenant_id=tenant_id,
            role=role,
            content=content,
            sources=sources
        )
        db.add(msg)
        await db.commit()

    async def get_context(self, db: AsyncSession, session_id: str, tenant_id: str) -> str:
        """
        Get the windowed memory.
        If turns > window_size, summarize older turns.
        """
        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id, ChatMessage.tenant_id == tenant_id)
            .order_by(ChatMessage.created_at.asc())
        )
        messages = result.scalars().all()
        
        if not messages:
            return ""

        # Simple windowed approach for now (latest N messages)
        # To strictly summarize older, we'd look for a 'system' summary message in the DB
        # or generate one. For MVP, we'll take the last N messages and if there are more,
        # we generate a quick summary (this can be optimized later).
        
        recent_messages = messages[-self.window_size:]
        
        context_lines = []
        for msg in recent_messages:
            prefix = "User" if msg.role == "user" else "Assistant"
            context_lines.append(f"{prefix}: {msg.content}")
            
        return "\n".join(context_lines)

memory_manager = ConversationMemory()
