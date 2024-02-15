from datetime import datetime, timedelta
from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt

from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_session

from models.users import User, UserRole

from services.users import get_user, verify_password

from schemas.auth import TokenData

from config import AuthConfig


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth_v1/token")


async def authenticate_user(database, email: str, password: str):
    user = await get_user(database, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, AuthConfig.SECRET_KEY, algorithm=AuthConfig.ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, AuthConfig.SECRET_KEY, algorithms=[AuthConfig.ALGORITHM])
        id: int = int(payload.get("sub"))

        if id is None:
            return None
        token_data = TokenData(id=id)
        return token_data
    except JWTError:
        return None


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], 
                           session: AsyncSession = Depends(get_session)):
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
