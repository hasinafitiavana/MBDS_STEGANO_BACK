from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.signatureimage import SignatureImage
from app.repositories.base_repository import BaseRepository
from typing import List

class SignatureImageRepository(BaseRepository[SignatureImage]):
    def __init__(self):
        super().__init__(SignatureImage)
    
    async def get_by_user_id(self, db: AsyncSession, user_id: int) -> List[SignatureImage]:
        result = await db.execute(select(SignatureImage).where(SignatureImage.id_user == user_id))
        return result.scalars().all()
