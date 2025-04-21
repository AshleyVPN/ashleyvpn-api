from abc import ABC, abstractmethod
from typing import Optional, List
from models.users import User, Referals, Sources
from repositories.base_repository import BaseRepository

class AbstractUserRepository(BaseRepository, ABC):
    """
    Абстрактный класс для репозитория пользователей.
    Определяет методы, которые должны быть реализованы в конкретных репозиториях пользователей.
    """
    
    @abstractmethod
    async def create_user(self, username: str, email: Optional[str] = None, 
                   telegram_id: Optional[int] = None, password: Optional[str] = None, 
                   is_admin: bool = False) -> User:
        pass

    @abstractmethod
    async def get_user(self, user_id: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def get_user_by_username(self, username: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        pass

    @abstractmethod
    async def get_all_users(self) -> List[User]:
        pass

    @abstractmethod
    async def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        pass

    @abstractmethod
    async def delete_user(self, user_id: str) -> bool:
        pass
    
    # Методы для работы с рефералами
    @abstractmethod
    async def create_referal(self, parent_id: str, child_id: str) -> Referals:
        pass
    
    @abstractmethod
    async def get_user_referals(self, parent_id: str) -> List[Referals]:
        pass
    
    # Методы для работы с источниками
    @abstractmethod
    async def create_source(self, name: str) -> Sources:
        pass
    
    @abstractmethod
    async def get_source(self, source_id: int) -> Optional[Sources]:
        pass
    
    @abstractmethod
    async def get_source_by_src_id(self, src_id: str) -> Optional[Sources]:
        pass
    
    @abstractmethod
    async def get_all_sources(self) -> List[Sources]:
        pass