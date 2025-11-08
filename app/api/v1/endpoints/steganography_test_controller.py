from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from app.core.database import get_session
from app.schemas.stego_schema import SteganoReponse, SteganoRequest, SteganoExtractReponse,SteganoExtractRequest
from app.services.steganography.f5_steganography_service import F5_stegano

router = APIRouter()

MIME_TYPES = {
    "png": "image/png",
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
}

@router.post("/hide", response_model=SteganoReponse, status_code=201)
async def hideMessage(
    image: Annotated[UploadFile, File(description="Le fichier image (PNG ou JPEG)")],
    secret_message: Annotated[str, Form(description="Le message secret à cacher")],
    format_output: Annotated[str, Form(description="Le format de sortie de l'image ('JPEG', 'png')")],
    db: AsyncSession = Depends(get_session)
):
    image_bytes = await image.read()
    stego_bytes = F5_stegano.hideSecretMessageInImage(
        image_bytes, 
        secret_message, 
        format_output
    )
    print("---------------------------------------------------------------------------------")
    output_format = format_output.lower().lstrip('.')
    media_type = MIME_TYPES.get(output_format.lower, "application/octet-stream")
    filename = f"stego_image.{output_format}"
    return Response(
        content=stego_bytes, 
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename=\"{filename}\""
        }
    )


@router.post("/extract", response_model=SteganoExtractReponse, status_code=201)
async def extractMessage(
    stego_image: Annotated[UploadFile, File(description="L'image stéganographiée (JPEG)")],
    db: AsyncSession = Depends(get_session)
):
    stego_bytes = await stego_image.read()
    secret_message = F5_stegano.extractSecretMessageFromImage(stego_bytes)
    return SteganoExtractReponse(secret_message=secret_message)

    
