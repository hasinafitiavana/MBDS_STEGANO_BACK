from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.repositories.signatureimage_repository import SignatureImageRepository
from app.repositories.user_repository import UserRepository
from app.models.signatureimage import SignatureImage
from app.schemas.signatureimage import SignatureImageCreate, SignatureImageUpdate
from typing import List, Optional


class SignatureImageService:
    def __init__(self):
        self.signatureimage_repository = SignatureImageRepository()
        self.user_repository = UserRepository()

    async def create_signature_image(self, db: AsyncSession, signature_data: SignatureImageCreate) -> SignatureImage:
        user = await self.user_repository.get_by_id(db, signature_data.id_user)
        if not user:
            raise ValueError("User not found")

        try:
            return await self.signatureimage_repository.create(db, **signature_data.dict())
        except IntegrityError:
            await db.rollback()
            raise ValueError("Error creating signature image")

    async def get_signature_image_by_id(self, db: AsyncSession, signature_id: int) -> Optional[SignatureImage]:
        return await self.signatureimage_repository.get_by_id(db, signature_id)

    async def get_signature_images(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[SignatureImage]:
        return await self.signatureimage_repository.get_all(db, skip=skip, limit=limit)

    async def get_signature_images_by_user(self, db: AsyncSession, user_id: int) -> List[SignatureImage]:
        return await self.signatureimage_repository.get_by_user_id(db, user_id)

    async def update_signature_image(self, db: AsyncSession, signature_id: int, signature_data: SignatureImageUpdate) -> \
            Optional[SignatureImage]:
        update_data = signature_data.dict(exclude_unset=True)

        if "id_user" in update_data:
            user = await self.user_repository.get_by_id(db, update_data["id_user"])
            if not user:
                raise ValueError("User not found")

        try:
            return await self.signatureimage_repository.update(db, signature_id, **update_data)
        except IntegrityError:
            await db.rollback()
            raise ValueError("Error updating signature image")

    async def delete_signature_image(self, db: AsyncSession, signature_id: int) -> bool:
        return await self.signatureimage_repository.delete(db, signature_id)


signature_image_service = SignatureImageService()
