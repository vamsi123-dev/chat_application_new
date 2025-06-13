from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Request, HTTPException, status
from typing import Dict, List
import json
from .. import models
from backend import database
from sqlalchemy.orm import Session
from ..routers.auth import get_current_user

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, ticket_id: int):
        await websocket.accept()
        if ticket_id not in self.active_connections:
            self.active_connections[ticket_id] = []
        self.active_connections[ticket_id].append(websocket)

    def disconnect(self, websocket: WebSocket, ticket_id: int):
        if ticket_id in self.active_connections:
            self.active_connections[ticket_id].remove(websocket)
            if not self.active_connections[ticket_id]:
                del self.active_connections[ticket_id]

    async def broadcast_to_ticket(self, message: str, ticket_id: int):
        if ticket_id in self.active_connections:
            for connection in self.active_connections[ticket_id]:
                await connection.send_text(message)

manager = ConnectionManager()

async def get_websocket_user(websocket: WebSocket, db: Session = Depends(database.get_db)):
    session = websocket.cookies.get("session")
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Get user from session
    user_id = websocket.state.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

@router.websocket("/ws/{ticket_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    ticket_id: int,
    db: Session = Depends(database.get_db)
):
    # Authenticate user
    try:
        user = await get_websocket_user(websocket, db)
    except HTTPException:
        await websocket.close(code=1008)  # Policy violation
        return

    # Check if user has access to this ticket
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        await websocket.close(code=1008)
        return
    
    if not user.is_admin and ticket.user_id != user.id:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, ticket_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Save message to database
            db_message = models.Message(
                content=message_data.get("content", ""),
                ticket_id=ticket_id,
                user_id=user.id
            )
            db.add(db_message)
            db.commit()
            
            # Broadcast message to all connected clients for this ticket
            await manager.broadcast_to_ticket(
                json.dumps({
                    "content": message_data.get("content", ""),
                    "user_id": user.id,
                    "username": user.username,
                    "timestamp": db_message.created_at.isoformat()
                }),
                ticket_id
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket, ticket_id)
        await manager.broadcast_to_ticket(
            json.dumps({
                "type": "disconnect",
                "user_id": user.id,
                "username": user.username
            }),
            ticket_id
        )