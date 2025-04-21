import asyncio
import uvicorn

from fastapi import FastAPI

from routers.api_routes import get_api_routers
from dependencies import emiter
from config import FastAPIConfig


def init_app():
    app = FastAPI()

    for router in get_api_routers():
        app.include_router(router)
    
    return app


app = init_app()


# @app.on_event("startup")
# async def startup_event():
#     asyncio.create_task(emiter.reader())


if __name__ == '__main__':
    uvicorn.run("main:app", port=int(FastAPIConfig.PORT), host=FastAPIConfig.HOST, reload=True)
