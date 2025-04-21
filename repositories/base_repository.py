from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession

class BaseRepository(ABC):
    """
    Абстрактный базовый класс для всех репозиториев.
    Определяет общий интерфейс и функциональность для работы с базой данных.
    """
    def __init__(self, db: AsyncSession):
        self.db = db