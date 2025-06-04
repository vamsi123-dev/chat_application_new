import os
from app.database import engine
from app.models import Base

# Remove existing database
if os.path.exists("support_chat.db"):
    os.remove("support_chat.db")

# Create new database with updated schema
Base.metadata.create_all(bind=engine)

print("Database recreated successfully!") 