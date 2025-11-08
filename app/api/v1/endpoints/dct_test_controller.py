from fastapi import APIRouter, UploadFile, File, Form, Response, HTTPException
from typing import Annotated
import cv2
import numpy as np

from app.schemas.stego_schema import SteganoReponse, SteganoExtractReponse
from app.services.steganography.dct_steganographie_service import dctSteganographieService

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
):
    image_bytes = await image.read()

    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Impossible de décoder l'image uploadée")

    output_ext = (format_output or "png").lower().lstrip('.')
    ext = f".{output_ext}"

    stego_img = dctSteganographieService.embed_dct(img, secret_message)

    success, buf = cv2.imencode(ext, stego_img)
    if not success:
        raise HTTPException(status_code=500, detail="Erreur lors de l'encodage de l'image stégo")
    stego_bytes = buf.tobytes()

    media_type = MIME_TYPES.get(output_ext, "application/octet-stream")
    filename = f"stegano_image.{output_ext}"
    return Response(
        content=stego_bytes,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename=\"{filename}\""
        }
    )

@router.post("/extract", response_model=SteganoExtractReponse, status_code=201)
async def extractMessage(
    stego_image: Annotated[UploadFile, File(description="L'image stéganographiée (PNG ou JPEG)")],
):
    image_bytes = await stego_image.read()

    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Impossible de décoder l'image uploadée")

    secret_message = dctSteganographieService.extract_dct(img)
    return SteganoExtractReponse(secret_message=secret_message)