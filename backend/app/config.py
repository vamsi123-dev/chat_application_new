from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./support_chat.db"
    secret_key: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    admin_security_code: str = "ADMIN123"  # This should be changed in production

settings = Settings() 