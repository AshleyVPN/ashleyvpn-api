from redis import Redis
from typing import Optional
from uuid import UUID, uuid4
from dataclasses import dataclass, asdict

from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(kw_only=True)
class PaymentRedis:
    id: UUID
    user_id: str


def create_to_redis(user_id: str, redis_connection: Redis) -> PaymentRedis:
    payment = PaymentRedis(id=uuid4(), user_id=user_id)

    redis_connection.hset(str(payment.id), mapping=asdict(payment))

    return payment


def find_from_redis(payment_id: str, redis_connection: Redis) -> PaymentRedis:
    payment_redis = redis_connection.hgetall(payment_id)

    payment = PaymentRedis(**payment_redis)

    return payment
