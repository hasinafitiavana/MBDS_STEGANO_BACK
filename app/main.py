from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.router import router as api_router
from app.core.init_db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown

app = FastAPI(
    title="Stegano API",
    description="API for steganography application",
    version="1.0.0",
    lifespan=lifespan
)

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

@app.get("/")
async def root():
    return {"message": "Stegano API is running"}
