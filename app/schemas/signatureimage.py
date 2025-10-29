from pydantic import BaseModel
from typing import Optional
from datetime import date

class SignatureImageBase(BaseModel):
    id_user: int
    signature: str

class SignatureImageCreate(SignatureImageBase):
    pass

class SignatureImageUpdate(BaseModel):
    id_user: Optional[int] = None
    signature: Optional[str] = None

class SignatureImageResponse(SignatureImageBase):
    id: int
    datesignature: date
    
    class Config:
        from_attributes = True
