from app.core.database import engine
from app.models.users import User
from app.models.signatureimage import SignatureImage
from app.models import Base

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Connexion base ")