from models.users import User, UserRole

from typing import Tuple, Optional, Annotated

from models.users import UserRole

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from passlib.context import CryptContext


class UserAlreadyExists(BaseException):
    pass


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(session, username: str | None = None, user_id: int | None = None) -> Optional[User]:
    try:
        user = await session.execute(select(User).where((User.username == username) | (User.id == user_id)))
        user = user.scalars().one()
        if user is not None:
            return user
    except NoResultFound:
        return None


async def create_user(
        session, username: str, password: str, 
) -> Tuple[Optional[User], Optional[BaseException]]:
    user = await get_user(session, username)

    if user is None:
        password_hash = get_password_hash(password)

        new_user = User(
            username=username, password=password_hash,
        )
        session.add(new_user)
        await session.commit()

        return new_user, None
    else:
        return None, UserAlreadyExists("User already exists")
