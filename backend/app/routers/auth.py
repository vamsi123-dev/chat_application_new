from fastapi import APIRouter, HTTPException, status, Request, Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import Optional
from pydantic import BaseModel
from .. import models, schemas
from backend import database
from ..config import settings
from ..utils import verify_password

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Simple login request model with only username and password
class LoginRequest(BaseModel):
    username: str
    password: str

async def get_current_user(request: Request, db: Session = Depends(database.get_db)):
    if "user_id" not in request.session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    user = db.query(models.User).filter(models.User.id == request.session["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # Check if username already exists
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if email already exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # If registering as admin, verify security code
    if user.is_admin:
        if not user.security_code or user.security_code != settings.admin_security_code:
            raise HTTPException(status_code=400, detail="Invalid security code for admin registration")

    # Create new user
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_admin=user.is_admin
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {
        "success": True,
        "message": "Registration successful",
        
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "is_admin": db_user.is_admin
        
    }



@router.post("/login")
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(database.get_db)
):
    # First check if user exists
    user = db.query(models.User).filter(models.User.username == login_data.username).first()
    if not user:
        # Log failed login attempt
        login_history = models.LoginHistory(
            user_id=None,
            ip_address=request.client.host,
            success=False
        )
        db.add(login_history)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username"
        )

    # Then check if password is correct
    if not verify_password(login_data.password, user.hashed_password):
        # Log failed login attempt
        login_history = models.LoginHistory(
            user_id=user.id,
            ip_address=request.client.host,
            success=False
        )
        db.add(login_history)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )

    # Log successful login
    login_history = models.LoginHistory(
        user_id=user.id,
        ip_address=request.client.host,
        success=True
    )
    db.add(login_history)
    db.commit()

    # Store user info in session
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    request.session["is_admin"] = user.is_admin

    return {
        "success": True,
        "message": "Login successful",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin
        }
    }

