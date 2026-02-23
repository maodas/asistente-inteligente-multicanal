from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class SenderType(str, enum.Enum):
    CUSTOMER = "customer"
    BOT = "bot"
    HUMAN = "human"

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender = Column(Enum(SenderType), nullable=False)
    content = Column(Text, nullable=False)
    intent_detected = Column(String, nullable=True)  # Para depuración
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")