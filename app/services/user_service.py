from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.repositories.user_repository import UserRepository
from app.models.users import User
from app.schemas.users import UserCreate, UserUpdate
from typing import List, Optional


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()

    async def create_user(self, db: AsyncSession, user_data: UserCreate) -> User:
        if await self.user_repository.login_exists(db, user_data.login):
            raise ValueError("Login already exists")

        try:
            return await self.user_repository.create(db, **user_data.dict())
        except IntegrityError:
            await db.rollback()
            raise ValueError("Login already exists")

    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        return await self.user_repository.get_by_id(db, user_id)

    async def get_user_by_login(self, db: AsyncSession, login: str) -> Optional[User]:
        return await self.user_repository.get_by_login(db, login)

    async def get_users(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        return await self.user_repository.get_all(db, skip=skip, limit=limit)

    async def update_user(self, db: AsyncSession, user_id: int, user_data: UserUpdate) -> Optional[User]:
        update_data = user_data.dict(exclude_unset=True)

        if "login" in update_data:
            if await self.user_repository.login_exists(db, update_data["login"], exclude_id=user_id):
                raise ValueError("Login already exists")

        try:
            return await self.user_repository.update(db, user_id, **update_data)
        except IntegrityError:
            await db.rollback()
            raise ValueError("Login already exists")

    async def delete_user(self, db: AsyncSession, user_id: int) -> bool:
        return await self.user_repository.delete(db, user_id)


user_service = UserService()
