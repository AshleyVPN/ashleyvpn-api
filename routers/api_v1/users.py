from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from dependencies import get_session
from services.users_service import UserService
from .schemas.users_schemas import UserCreate, UserUpdate, UserResponse, ReferalCreate, ReferalResponse, SourceCreate, SourceResponse
from models.users import User, Referals, Sources

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, session: AsyncSession = Depends(get_session)):
    user_service = UserService(session)
    return await user_service.create_user(
        username=user.username,
        email=user.email,
        telegram_id=user.telegram_id,
        password=user.password,
        is_admin=user.is_admin
    )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, session: AsyncSession = Depends(get_session)):
    user_service = UserService(session)
    return await user_service.get_user(user_id)

@router.get("/by-username/{username}", response_model=UserResponse)
async def get_user_by_username(username: str, session: AsyncSession = Depends(get_session)):
    user_service = UserService(session)
    return await user_service.get_user_by_username(username)

@router.get("/by-email/{email}", response_model=UserResponse)
async def get_user_by_email(email: str, session: AsyncSession = Depends(get_session)):
    user_service = UserService(session)
    return await user_service.get_user_by_email(email)

@router.get("/by-telegram/{telegram_id}", response_model=UserResponse)
async def get_user_by_telegram_id(telegram_id: int, session: AsyncSession = Depends(get_session)):
    user_service = UserService(session)
    return await user_service.get_user_by_telegram_id(telegram_id)

@router.get("/", response_model=List[UserResponse])
async def get_all_users(session: AsyncSession = Depends(get_session)):
    user_service = UserService(session)
    return await user_service.get_all_users()

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_data: UserUpdate, session: AsyncSession = Depends(get_session)):
    user_service = UserService(session)
    return await user_service.update_user(
        user_id,
        **user_data.dict(exclude_unset=True)
    )

@router.delete("/{user_id}")
async def delete_user(user_id: str, session: AsyncSession = Depends(get_session)):
    user_service = UserService(session)
    return await user_service.delete_user(user_id)

# Эндпоинты для рефералов
@router.post("/referals", response_model=ReferalResponse)
async def create_referal(referal: ReferalCreate, session: AsyncSession = Depends(get_session)):
    user_service = UserService(session)
    return await user_service.create_referal(referal.parent, referal.child)

@router.get("/referals/{parent_id}", response_model=List[ReferalResponse])
async def get_user_referals(parent_id: str, session: AsyncSession = Depends(get_session)):
    user_service = UserService(session)
    return await user_service.get_user_referals(parent_id)

# Эндпоинты для источников
@router.post("/sources", response_model=SourceResponse)
async def create_source(source: SourceCreate, session: AsyncSession = Depends(get_session)):
    user_service = UserService(session)
    return await user_service.create_source(source.name)

@router.get("/sources/{source_id}", response_model=SourceResponse)
async def get_source(source_id: int, session: AsyncSession = Depends(get_session)):
    user_service = UserService(session)
    return await user_service.get_source(source_id)

@router.get("/sources/by-src-id/{src_id}", response_model=SourceResponse)
async def get_source_by_src_id(src_id: str, session: AsyncSession = Depends(get_session)):
    user_service = UserService(session)
    return await user_service.get_source_by_src_id(src_id)

@router.get("/sources", response_model=List[SourceResponse])
async def get_all_sources(session: AsyncSession = Depends(get_session)):
    user_service = UserService(session)
    return await user_service.get_all_sources()