import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

from redis_events import RedisEventEmiter
from config import RedisConfig, RedisEventsConfig

from database import async_session


redis_client = redis.Redis(
    host=RedisConfig.REDIS_HOST,
    port=RedisConfig.REDIS_PORT,
    db=RedisConfig.REDIS_DB,
    password=RedisConfig.REDIS_PASS,
    decode_responses=True,    
)


redis_events = redis.Redis(
    host=RedisEventsConfig.REDIS_HOST,
    port=RedisEventsConfig.REDIS_PORT,
    db=RedisEventsConfig.REDIS_DB,
    password=RedisEventsConfig.REDIS_PASS,
    decode_responses=True,    
)


emiter = RedisEventEmiter(redis_events, channels=[])


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
