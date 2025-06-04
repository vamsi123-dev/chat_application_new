from sqlalchemy import Column, Integer, String, DateTime, Text
from database import Base
import datetime

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, index=True)
    sender_id = Column(String, index=True)
    receiver_id = Column(String, index=True)
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    message_type = Column(String, default="text")
    is_read = Column(Integer, default=0)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, unique=True, index=True)
    customer_id = Column(String, index=True)
    service_provider_id = Column(String, index=True)
    service_type = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow) 