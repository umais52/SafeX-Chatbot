from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ForeignKey, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    tenant_id = Column(String, index=True, nullable=False)
    role = Column(String, nullable=False) # "user", "assistant", "system"
    content = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True) # Storing attribution
    created_at = Column(DateTime, default=datetime.utcnow)

class Escalation(Base):
    __tablename__ = "escalations"
    
    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    tenant_id = Column(String, index=True, nullable=False)
    user_id = Column(String, nullable=False)
    query = Column(Text, nullable=False)
    context = Column(JSON, nullable=True) # Recent conversation history
    status = Column(String, default="pending") # pending, resolved
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)


class BotAnsweredQuestion(Base):
    """Stores every question the bot successfully answered, for clustering."""
    __tablename__ = "bot_answered_questions"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, index=True, nullable=False)
    session_id = Column(String, nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    is_clustered = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class GeneratedFAQ(Base):
    """Auto-generated FAQs from the clustering pipeline."""
    __tablename__ = "generated_faqs"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, index=True, nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    source_cluster_size = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

