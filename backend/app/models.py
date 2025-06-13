from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    is_admin = Column(Boolean, default=False)
    login_history = relationship("LoginHistory", back_populates="user")
    tickets = relationship("Ticket", back_populates="user")
    messages = relationship("Message", back_populates="user")

class LoginHistory(Base):
    __tablename__ = "login_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ip_address = Column(String(255))
    login_time = Column(DateTime, default=datetime.utcnow)
    success = Column(Boolean, default=False)
    user = relationship("User", back_populates="login_history")

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    description = Column(String(255))
    status = Column(String(255), default="open")
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="tickets")
    messages = relationship("Message", back_populates="ticket")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    ticket = relationship("Ticket", back_populates="messages")
    user = relationship("User", back_populates="messages")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(255), unique=True, index=True)
    customer_id = Column(String(255), index=True)
    service_provider_id = Column(String(255), index=True)
    service_type = Column(String(255))
    status = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    messages = relationship("ChatMessage", back_populates="order")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(255), ForeignKey("orders.order_id"), index=True)
    sender_id = Column(String(255), index=True)
    receiver_id = Column(String(255), index=True)
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    message_type = Column(String(255), default="text")
    is_read = Column(Integer, default=0)
    order = relationship("Order", back_populates="messages") 