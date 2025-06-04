from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, database
from ..routers.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class MessageBase(BaseModel):
    content: str
    ticket_id: int

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/messages/", response_model=MessageResponse)
def create_message(
    message: MessageCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify ticket exists and user has access
    ticket = db.query(models.Ticket).filter(models.Ticket.id == message.ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if not current_user.is_admin and ticket.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this ticket")

    db_message = models.Message(
        content=message.content,
        ticket_id=message.ticket_id,
        user_id=current_user.id
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

@router.get("/messages/{ticket_id}", response_model=List[MessageResponse])
def get_messages(
    ticket_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify ticket exists and user has access
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if not current_user.is_admin and ticket.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this ticket")

    messages = db.query(models.Message).filter(models.Message.ticket_id == ticket_id).all()
    return messages 