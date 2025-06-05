from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from backend.app.routers import auth, tickets, messages, websocket
from backend.app.database import engine, Base
from backend.app import models
from backend.app.config import settings
from sqlalchemy import text
from sqlalchemy.exc import OperationalError


# Create tables
Base.metadata.create_all(bind=engine)

with engine.connect() as connection:
    connection.execute(text("SELECT 1"))


from sqlalchemy.exc import OperationalError

try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))  # wrap string with text()
    print("✅ Database connection successful.")
except OperationalError as e:
    print("❌ Database connection failed:", e)


app = FastAPI(title="Support Chat API")


# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie="session",
    same_site="lax",
    https_only=False  # Changed to False for development
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(tickets.router, prefix="/api", tags=["Tickets"])
app.include_router(messages.router, prefix="/api", tags=["Messages"])
app.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Support Chat API"} 