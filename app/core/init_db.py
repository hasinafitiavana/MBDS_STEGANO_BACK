from app.core.database import engine
from app.models.story import StoryORM

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(StoryORM.metadata.create_all)
    print("✅ Tables créées avec succès")