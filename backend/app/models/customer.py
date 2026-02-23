from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True, nullable=True)  # Para WhatsApp
    session_id = Column(String, unique=True, index=True, nullable=True)    # Para web
    name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())