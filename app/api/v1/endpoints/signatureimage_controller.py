from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_session
from app.services.signatureimage_service import signature_image_service
from app.schemas.signatureimage import SignatureImageCreate, SignatureImageUpdate, SignatureImageResponse

router = APIRouter()


@router.post("/", response_model=SignatureImageResponse, status_code=201)
async def create_signature_image(
        signature_data: SignatureImageCreate,
        db: AsyncSession = Depends(get_session)
):
    try:
        signature = await signature_image_service.create_signature_image(db, signature_data)
        return signature
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[SignatureImageResponse])
async def get_signature_images(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_session)
):
    try:
        signatures = await signature_image_service.get_signature_images(db, skip=skip, limit=limit)
        return signatures
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{signature_id}", response_model=SignatureImageResponse)
async def get_signature_image(
        signature_id: int,
        db: AsyncSession = Depends(get_session)
):
    try:
        signature = await signature_image_service.get_signature_image_by_id(db, signature_id)
        if not signature:
            raise HTTPException(status_code=404, detail="Signature image not found")
        return signature
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}", response_model=List[SignatureImageResponse])
async def get_signature_images_by_user(
        user_id: int,
        db: AsyncSession = Depends(get_session)
):
    try:
        signatures = await signature_image_service.get_signature_images_by_user(db, user_id)
        return signatures
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{signature_id}", response_model=SignatureImageResponse)
async def update_signature_image(
        signature_id: int,
        signature_data: SignatureImageUpdate,
        db: AsyncSession = Depends(get_session)
):
    try:
        signature = await signature_image_service.update_signature_image(db, signature_id, signature_data)
        if not signature:
            raise HTTPException(status_code=404, detail="Signature image not found")
        return signature
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{signature_id}", status_code=204)
async def delete_signature_image(
        signature_id: int,
        db: AsyncSession = Depends(get_session)
):
    try:
        deleted = await signature_image_service.delete_signature_image(db, signature_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Signature image not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
