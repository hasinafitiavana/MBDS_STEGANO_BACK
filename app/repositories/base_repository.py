from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update
from typing import TypeVar, Generic, Type, Optional, List, Any, Dict
from app.models import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    async def create(self, db: AsyncSession, **kwargs) -> ModelType:
        db_obj = self.model(**kwargs)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_by_id(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()
    
    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ModelType]:
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()
    
    async def update(self, db: AsyncSession, id: int, **kwargs) -> Optional[ModelType]:
        db_obj = await self.get_by_id(db, id)
        if not db_obj:
            return None
        
        for key, value in kwargs.items():
            setattr(db_obj, key, value)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete(self, db: AsyncSession, id: int) -> bool:
        db_obj = await self.get_by_id(db, id)
        if not db_obj:
            return False
        
        await db.delete(db_obj)
        await db.commit()
        return True
    
    async def get_by_field(self, db: AsyncSession, field: str, value: Any) -> Optional[ModelType]:
        result = await db.execute(select(self.model).where(getattr(self.model, field) == value))
        return result.scalar_one_or_none()
