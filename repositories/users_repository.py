from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.users import User, Referals, Sources
from typing import Optional, List
from datetime import datetime
import uuid

from repositories.abstract_users_repository import AbstractUserRepository

class UserRepository(AbstractUserRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, username: str, email: Optional[str] = None, 
                   telegram_id: Optional[int] = None, password: Optional[str] = None, 
                   is_admin: bool = False) -> User:
        user = User(
            username=username,
            email=email,
            telegram_id=telegram_id,
            password=password,
            is_admin=is_admin
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_user(self, user_id: str) -> Optional[User]:
        result = await self.db.execute(select(User).filter(User.id == user_id))
        return result.scalars().first()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(select(User).filter(User.username == username))
        return result.scalars().first()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalars().first()
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).filter(User.telegram_id == telegram_id))
        return result.scalars().first()

    async def get_all_users(self) -> List[User]:
        result = await self.db.execute(select(User))
        return result.scalars().all()

    async def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        user = await self.get_user(user_id)
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            await self.db.commit()
            await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: str) -> bool:
        user = await self.get_user(user_id)
        if user:
            await self.db.delete(user)
            await self.db.commit()
            return True
        return False
    
    # Методы для работы с рефералами
    async def create_referal(self, parent_id: str, child_id: str) -> Referals:
        referal = Referals(
            parent=parent_id,
            child=child_id
        )
        self.db.add(referal)
        await self.db.commit()
        await self.db.refresh(referal)
        return referal
    
    async def get_user_referals(self, parent_id: str) -> List[Referals]:
        result = await self.db.execute(select(Referals).filter(Referals.parent == parent_id))
        return result.scalars().all()
    
    # Методы для работы с источниками
    async def create_source(self, name: str) -> Sources:
        source = Sources(name=name)
        self.db.add(source)
        await self.db.commit()
        await self.db.refresh(source)
        return source
    
    async def get_source(self, source_id: int) -> Optional[Sources]:
        result = await self.db.execute(select(Sources).filter(Sources.id == source_id))
        return result.scalars().first()
    
    async def get_source_by_src_id(self, src_id: str) -> Optional[Sources]:
        result = await self.db.execute(select(Sources).filter(Sources.src_id == src_id))
        return result.scalars().first()
    
    async def get_all_sources(self) -> List[Sources]:
        result = await self.db.execute(select(Sources))
        return result.scalars().all()