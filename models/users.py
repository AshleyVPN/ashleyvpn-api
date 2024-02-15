from .base import Base

from datetime import datetime
from sqlalchemy import BigInteger, Integer, String,\
     Column, ForeignKey, Float, DateTime, Boolean

import uuid


def generate_ref_id(string_length=10):
     """Returns a random string of length string_length."""
     random = str(uuid.uuid4()) # Convert UUID format to a Python string.
     random = random.upper() # Make all characters uppercase.
     random = random.replace("-","") # Remove the UUID '-'.
     return random[0:string_length] # Return the random string.


class User(Base):
     __tablename__ = 'users'
     id = Column(String, primary_key=True, default=str(uuid.uuid4()))
     telegram_id = Column(BigInteger, unique=True, nullable=True)
     is_admin = Column(Boolean, default=False)
     joined_at = Column(DateTime, default=datetime.now(), nullable=True)
     ref_id = Column(String, default=generate_ref_id(), unique=True, nullable=True)
     source_id = Column(ForeignKey('sources.id', ondelete='SET NULL'), nullable=True)
     username = Column(String, unique=True, nullable=False)
     email = Column(String, unique=True, nullable=True)
     password = Column(String, unique=False, nullable=True)


class Referals(Base):
     __tablename__ = 'referals'
     id = Column(String, primary_key=True, default=str(uuid.uuid4()))
     parent = Column(ForeignKey('users.id'), nullable=True)
     child = Column(ForeignKey('users.id'), nullable=True)


class Sources(Base):
     __tablename__ = 'sources'
     id = Column(Integer, primary_key=True, autoincrement=True)
     name = Column(String)
     src_id = Column(String, default=generate_ref_id(), unique=True, nullable=True)