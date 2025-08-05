from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.models.users import User
from app.schemas.users import UserCreate, UserUpdate
from typing import List, Optional

class UserService:
    
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        try:
            db_user = User(**user_data.dict())
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
            return db_user
        except IntegrityError:
            await db.rollback()
            raise ValueError("Login already exists")
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_login(db: AsyncSession, login: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.login == login))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        result = await db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()
    
    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> Optional[User]:
        db_user = await UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        try:
            await db.commit()
            await db.refresh(db_user)
            return db_user
        except IntegrityError:
            await db.rollback()
            raise ValueError("Login already exists")
    
    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> bool:
        db_user = await UserService.get_user_by_id(db, user_id)
        if not db_user:
            return False
        
        await db.delete(db_user)
        await db.commit()
        return True
