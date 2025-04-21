from typing import Optional, List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.users_repository import UserRepository
from models.users import User, Referals, Sources
from services.users import get_password_hash, verify_password

class UserService:
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    async def create_user(self, username: str, email: Optional[str] = None, 
                        telegram_id: Optional[int] = None, password: Optional[str] = None, 
                        is_admin: bool = False) -> User:
        try:
            # Проверка на существование пользователя с таким же username или email
            if await self.repository.get_user_by_username(username):
                raise HTTPException(status_code=400, detail="Username already registered")
            
            if email and await self.repository.get_user_by_email(email):
                raise HTTPException(status_code=400, detail="Email already registered")
            
            if telegram_id and await self.repository.get_user_by_telegram_id(telegram_id):
                raise HTTPException(status_code=400, detail="Telegram ID already registered")
            
            # Хеширование пароля, если он предоставлен
            hashed_password = None
            if password:
                hashed_password = get_password_hash(password)
            
            return await self.repository.create_user(
                username=username,
                email=email,
                telegram_id=telegram_id,
                password=hashed_password,
                is_admin=is_admin
            )
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=400, detail=str(e))

    async def get_user(self, user_id: str) -> Optional[User]:
        user = await self.repository.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        user = await self.repository.get_user_by_username(username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        user = await self.repository.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        user = await self.repository.get_user_by_telegram_id(telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def get_all_users(self) -> List[User]:
        return await self.repository.get_all_users()

    async def update_user(self, user_id: str, **kwargs) -> User:
        # Если обновляется пароль, хешируем его
        if 'password' in kwargs and kwargs['password']:
            kwargs['password'] = get_password_hash(kwargs['password'])
            
        user = await self.repository.update_user(user_id, **kwargs)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def delete_user(self, user_id: str) -> bool:
        if not await self.repository.delete_user(user_id):
            raise HTTPException(status_code=404, detail="User not found")
        return True
    
    # Методы для работы с рефералами
    async def create_referal(self, parent_id: str, child_id: str) -> Referals:
        try:
            # Проверка существования пользователей
            if not await self.repository.get_user(parent_id):
                raise HTTPException(status_code=404, detail="Parent user not found")
            
            if not await self.repository.get_user(child_id):
                raise HTTPException(status_code=404, detail="Child user not found")
            
            return await self.repository.create_referal(parent_id, child_id)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_user_referals(self, parent_id: str) -> List[Referals]:
        # Проверка существования пользователя
        if not await self.repository.get_user(parent_id):
            raise HTTPException(status_code=404, detail="User not found")
        
        return await self.repository.get_user_referals(parent_id)
    
    # Методы для работы с источниками
    async def create_source(self, name: str) -> Sources:
        try:
            return await self.repository.create_source(name)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_source(self, source_id: int) -> Optional[Sources]:
        source = await self.repository.get_source(source_id)
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        return source
    
    async def get_source_by_src_id(self, src_id: str) -> Optional[Sources]:
        source = await self.repository.get_source_by_src_id(src_id)
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        return source
    
    async def get_all_sources(self) -> List[Sources]:
        return await self.repository.get_all_sources()
        
    # Метод для проверки пароля пользователя
    async def verify_user_password(self, username: str, password: str) -> Optional[User]:
        user = await self.repository.get_user_by_username(username)
        if not user or not user.password:
            return None
        
        if verify_password(password, user.password):
            return user
        return None