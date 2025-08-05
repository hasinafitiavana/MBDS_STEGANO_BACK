from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.users import User
from app.repositories.base_repository import BaseRepository
from typing import Optional

class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)
    
    async def get_by_login(self, db: AsyncSession, login: str) -> Optional[User]:
        return await self.get_by_field(db, "login", login)
    
    async def login_exists(self, db: AsyncSession, login: str, exclude_id: Optional[int] = None) -> bool:
        query = select(User).where(User.login == login)
        if exclude_id:
            query = query.where(User.id != exclude_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None
