from datetime import datetime
from pydantic import BaseModel, EmailStr

# Schema for user registration (incoming data)
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# Schema for user login (incoming data)
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Schema for returning user data (outgoing response)
# Notice: NEVER include the password here!
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Allows Pydantic to read directly from SQLAlchemy models
