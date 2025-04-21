from datetime import datetime, timedelta
from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_session
from models.users import User
from services.users import get_user
from services.users_service import UserService
from routers.api_v1.schemas.auth_schemas import TokenData
from config import AuthConfig


# Настройка OAuth2 с указанием эндпоинта для получения токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api_v1/token")


async def authenticate_user(database: AsyncSession, email_or_username: str, password: str) -> Optional[User]:
    """
    Аутентификация пользователя по email/username и паролю
    
    Args:
        database: Асинхронная сессия базы данных
        email_or_username: Email или имя пользователя
        password: Пароль пользователя
        
    Returns:
        User: Объект пользователя при успешной аутентификации или False при неудаче
    """
    # Создаем экземпляр UserService
    user_service = UserService(database)
    
    # Проверяем, является ли введенное значение email или username
    try:
        # Сначала пробуем найти пользователя по username
        user = await user_service.verify_user_password(email_or_username, password)
        if user:
            return user
            
        # Если не нашли по username, пробуем по email
        if '@' in email_or_username:
            # Получаем пользователя по email
            try:
                user = await user_service.get_user_by_email(email_or_username)
                # Проверяем пароль
                if user and await user_service.verify_user_password(user.username, password):
                    return user
            except HTTPException:
                pass
                
        return False
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Создание JWT access токена
    
    Args:
        data: Данные для включения в токен
        expires_delta: Время жизни токена
        
    Returns:
        str: Закодированный JWT токен
    """
    to_encode = data.copy()
    
    # Устанавливаем время истечения токена
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, AuthConfig.SECRET_KEY, algorithm=AuthConfig.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Создание JWT refresh токена с более длительным сроком действия
    
    Args:
        data: Данные для включения в токен
        expires_delta: Время жизни токена
        
    Returns:
        str: Закодированный JWT токен
    """
    to_encode = data.copy()
    
    # Устанавливаем время истечения токена
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=AuthConfig.REFRESH_TOKEN_EXPIRE_DAYS)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, AuthConfig.SECRET_KEY, algorithm=AuthConfig.ALGORITHM)
    return encoded_jwt


def verify_refresh_token(token: str) -> Optional[dict]:
    """
    Проверка refresh токена
    
    Args:
        token: JWT токен для проверки
        
    Returns:
        dict: Данные из токена или None при ошибке
    """
    try:
        payload = jwt.decode(token, AuthConfig.SECRET_KEY, algorithms=[AuthConfig.ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_token(token: str) -> Optional[TokenData]:
    """
    Проверка access токена и извлечение данных пользователя
    
    Args:
        token: JWT токен для проверки
        
    Returns:
        TokenData: Данные из токена или None при ошибке
    """
    try:
        payload = jwt.decode(token, AuthConfig.SECRET_KEY, algorithms=[AuthConfig.ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            return None
            
        token_data = TokenData(id=user_id)
        return token_data
    except JWTError:
        return None


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], 
                           session: AsyncSession = Depends(get_session)) -> User:
    """
    Получение текущего пользователя по токену
    
    Args:
        token: JWT токен из заголовка Authorization
        session: Асинхронная сессия базы данных
        
    Returns:
        User: Объект пользователя
        
    Raises:
        HTTPException: Если токен недействителен или пользователь не найден
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_token(token)

    if token_data is None:
        raise credentials_exception

    user = await get_user(session, user_id=token_data.id)
    if user is None:
        raise credentials_exception
        
    return user


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Проверяет, что текущий пользователь является администратором
    
    Args:
        current_user: Текущий пользователь, полученный из токена
        
    Returns:
        User: Объект пользователя-администратора
        
    Raises:
        HTTPException: Если пользователь не является администратором
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администратор может выполнять эту операцию"
        )
    return current_user

