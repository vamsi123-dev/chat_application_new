from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from .. import models,  schemas
from backend import database
from ..routers.auth import get_current_user

from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class TicketBase(BaseModel):
    title: str

class TicketCreate(TicketBase):
    description: str

class TicketResponse(TicketBase):
    id: int
    status: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/Orders/", response_model=schemas.TicketResponse)
def create_ticket(
    ticket: schemas.TicketCreate,
    request: Request,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if user has any active tickets (status="open")
    active_ticket = db.query(models.Ticket).filter(
        models.Ticket.user_id == current_user.id,
        models.Ticket.status == "open"
    ).first()
    
    if active_ticket:
        raise HTTPException(
            status_code=400,
            detail="You already have an active ticket. Please wait for it to be resolved before creating a new one."
        )

    db_ticket = models.Ticket(
        title=ticket.title,
        description=ticket.description,
        user_id=current_user.id
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

@router.get("/Orders/", response_model=List[schemas.TicketResponse])
def get_tickets(
    request: Request,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.is_admin:
        tickets = db.query(models.Ticket).all()
    else:
        tickets = db.query(models.Ticket).filter(models.Ticket.user_id == current_user.id).all()
    return tickets

@router.get("/Orders/{ticket_id}", response_model=schemas.TicketResponse)
def get_ticket(
    ticket_id: int,
    request: Request,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if not current_user.is_admin and ticket.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this ticket")
    return ticket

@router.put("/Orders/{ticket_id}/status")
def update_ticket_status(
    ticket_id: int,
    status: str,
    request: Request,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Only admins can update ticket status"
        )
    
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket.status = status
    db.commit()
    return {"message": f"Ticket status updated to {status}"} 