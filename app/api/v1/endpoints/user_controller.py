from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_session
from app.services.user_service import user_service
from app.schemas.users import UserCreate, UserUpdate, UserResponse, LoginRequest, TokenResponse
from app.core.security import verify_password
from app.core.auth import create_access_token, revoke_token, bearer_scheme, get_current_user
from fastapi.security import HTTPAuthorizationCredentials

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
        user_data: UserCreate,
        db: AsyncSession = Depends(get_session)
):
    try:
        user = await user_service.create_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[UserResponse])
async def get_users(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_session)
):
    try:
        users = await user_service.get_users(db, skip=skip, limit=limit)
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
        user_id: int,
        db: AsyncSession = Depends(get_session)
):
    try:
        user = await user_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
        user_id: int,
        user_data: UserUpdate,
        db: AsyncSession = Depends(get_session)
):
    try:
        user = await user_service.update_user(db, user_id, user_data)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}", status_code=204)
async def delete_user(
        user_id: int,
        db: AsyncSession = Depends(get_session)
):
    try:
        deleted = await user_service.delete_user(db, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="User not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_session)):
    user = await user_service.get_user_by_login(db, credentials.login)
    if not user or not verify_password(credentials.mdp, user.mdp):
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_payload = UserResponse.from_orm(user).dict()
    token = create_access_token({"user": user_payload})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout")
async def logout(auth: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    revoke_token(auth.credentials)
    return {"detail": "Logged out"}
