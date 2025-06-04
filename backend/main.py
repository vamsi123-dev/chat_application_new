from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict
import json
from database import get_db, engine
import models

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)

manager = ConnectionManager()

@app.get("/")
def read_root():
    return {"message": "Chat API is running"}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, db: Session = Depends(get_db)):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Save message to database
            chat_message = models.ChatMessage(
                order_id=message_data["order_id"],
                sender_id=client_id,
                receiver_id=message_data["receiver_id"],
                message=message_data["message"],
                message_type=message_data.get("message_type", "text")
            )
            db.add(chat_message)
            db.commit()

            # Send message to receiver if online
            if message_data["receiver_id"] in manager.active_connections:
                await manager.send_personal_message(data, message_data["receiver_id"])

    except WebSocketDisconnect:
        manager.disconnect(client_id)

@app.get("/chat/{order_id}")
async def get_chat_history(order_id: str, db: Session = Depends(get_db)):
    messages = db.query(models.ChatMessage)\
        .filter(models.ChatMessage.order_id == order_id)\
        .order_by(models.ChatMessage.timestamp)\
        .all()
    
    return messages

@app.get("/orders/{user_id}")
async def get_user_orders(user_id: str, db: Session = Depends(get_db)):
    orders = db.query(models.Order)\
        .filter((models.Order.customer_id == user_id) | 
                (models.Order.service_provider_id == user_id))\
        .order_by(models.Order.created_at.desc())\
        .all()
    return orders

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 