from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.api.router import router as api_router
from app.core.init_db import init_db

# auth imports for middleware
from app.core.auth import decode_access_token, token_blacklist
from app.core.database import SessionLocal
from app.services.user_service import user_service

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


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to attach the current user (if any) to request.state.current_user.

    Behavior:
    - Reads Authorization header (Bearer token)
    - Skips if no header or token is blacklisted
    - Decodes token using `decode_access_token`
    - Loads user using an async DB session and `user_service.get_user_by_id`
    - Attaches user object or None to `request.state.current_user`
    """

    async def dispatch(self, request: Request, call_next):
        # default: no user
        request.state.current_user = None

        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            if token in token_blacklist:
                request.state.current_user = None
            else:
                try:
                    payload = decode_access_token(token)
                    user_id = payload.get("sub")
                    if user_id is not None:
                        # create an async session and fetch user
                        async with SessionLocal() as session:
                            user = await user_service.get_user_by_id(session, int(user_id))
                            request.state.current_user = user
                except Exception:
                    # don't raise here; keep current_user as None
                    request.state.current_user = None

        response = await call_next(request)
        return response


app.add_middleware(AuthMiddleware)
app.include_router(api_router, prefix='/api')

@app.get("/")
async def root():
    return {"message": "Stegano API is running"}
