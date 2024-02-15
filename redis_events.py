import redis.asyncio as redis
from functools import wraps
import json 


class RedisEventEmiter():
    _instance = None
    _subs = {}
    _channels = []
    _client = None

    def __init__(self, redis_client, channels=[]):
        self._channels = channels
        self._client = redis_client

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls) 
        return cls._instance

    def subscribe_on(self, event):
        def decorator(func):
            if self._subs.get(event) is None:
                self._subs[event] = []
            self._subs[event].append(func)
            return func
        return decorator

    async def emit(self, event, data):
        subs = self._subs.get(event)
        if subs is not None:
            for sub in subs:
                await sub(data)

    async def reader(self):
        async with self._client.pubsub(ignore_subscribe_messages=True) as pubsub:
            for channel in self._channels:
                await pubsub.subscribe(channel)
            
            async for message in pubsub.listen():
                if message is not None:
                    try:
                        data = json.loads(message['data'])
                    except json.JSONDecodeError:
                        continue
                    
                    type_event = data.get('type_event')
                    
                    await self.emit(type_event, data)
