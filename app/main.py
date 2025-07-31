from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router as api_router

from app.core import init_db, get_settings

app = FastAPI(
    title="Field Filler API"
)
settings = get_settings()
origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix='/api')

# Appeler init_db() au démarrage
@app.on_event("startup")
async def on_startup():
    await init_db()
