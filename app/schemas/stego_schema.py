import app.models.users
from pydantic import BaseModel
from typing import Optional

class SteganoRequest(BaseModel):
    image_data: bytes
    secret_message: str
    format_output: str

class SteganoReponse(BaseModel):
    stego_image_data: bytes
    image_format: str

class SteganoExtractRequest(BaseModel):
    stego_image_data: bytes

class SteganoExtractReponse(BaseModel):
    secret_message: str
    nom: str = None
    prenom: str = None

