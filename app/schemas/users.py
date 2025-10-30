from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    nom: str
    prenom: str
    login: str

class UserCreate(UserBase):
    mdp: str

class UserUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    login: Optional[str] = None
    mdp: Optional[str] = None

class UserResponse(UserBase):
    id: int
    
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    login: str
    mdp: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
