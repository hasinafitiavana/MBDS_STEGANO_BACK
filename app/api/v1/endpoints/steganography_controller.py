from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from app.core.database import get_session
from app.core.auth import get_current_user
from app.schemas.stego_schema import SteganoReponse, SteganoRequest, SteganoExtractReponse,SteganoExtractRequest
from app.services.steganography.f5_steganography_service import F5_stegano
from app.services.steganography.dct_steganographie_service import dctSteganographieService
from app.services.steganography.lsb_steganography_service import lsbSteganographieService
from app.services.cryptography.cryptography import SteganoCryptoService
from app.services.user_service import user_service
from app.core.config import get_settings
import cv2
import numpy as np

router = APIRouter()

MIME_TYPES = {
    "png": "image/png",
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
}

@router.post("/hide", response_model=SteganoReponse, status_code=201)
async def hideMessage(
    image: Annotated[UploadFile, File(description="Le fichier image (PNG ou JPEG)")],
    format_output: Annotated[str, Form(description="Le format de sortie de l'image ('JPEG', 'png')")],
    current_user: Annotated[object, Depends(get_current_user)] = None,
):
    user_id = current_user.id
    secret_message = SteganoCryptoService.encrypt_for_user(user_id)

    settings = get_settings()
    algo = (settings.STEGANO_ALGO or "F5").lower()

    image_bytes = await image.read()

    try:
        if algo == "f5":
            stego_bytes = F5_stegano.hideSecretMessageInImage(
                image_bytes,
                secret_message,
                format_output,
            )
        elif algo == "dct" or algo == "dct_stegano":
            stego_bytes = dctSteganographieService.hideSecretMessageInImage(
                image_bytes,
                secret_message,
                format_output
            )
        elif algo == "lsb":
            stego_bytes = lsbSteganographieService.hideSecretMessageInImage(
                image_bytes,
                secret_message,
                "png"
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported STEGANO_ALGO: {settings.STEGANO_ALGO}")
    except Exception:
        raise HTTPException(status_code=503, detail="Error when encoding the image");

    output_format = format_output.lower().lstrip('.')
    media_type = MIME_TYPES.get(output_format.lower(), "application/octet-stream")
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
    db: AsyncSession = Depends(get_session),
):
    stego_bytes = await stego_image.read()
    settings = get_settings()
    algo = (settings.STEGANO_ALGO or "F5").lower()

    try:
        if algo == "f5":
            secret_message = F5_stegano.extractSecretMessageFromImage(stego_bytes)
        elif algo == "dct" or algo == "dct_stegano":
            secret_message = dctSteganographieService.extractSecretMessageFromImage(stego_bytes)
        elif algo == "lsb":
            secret_message = lsbSteganographieService.extractSecretMessageFromImage(stego_bytes)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported STEGANO_ALGO: {settings.STEGANO_ALGO}")
    except Exception:
        raise HTTPException(status_code=503, detail="Error when extracting message")

    print("Extracted secret message:", secret_message);
    user_id = SteganoCryptoService.decrypt_for_user(secret_message)
    user = await user_service.get_user_by_id(db, int(user_id))
    print("Extracted user ID:", str(user.nom));
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return SteganoExtractReponse(nom=user.nom, prenom=user.prenom)

    
