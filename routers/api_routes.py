from fastapi import APIRouter

from .api_v1 import test, chats

routes = {
    'api_v1' : [
        test.router,
        chats.router,
    ]
}


def get_api_routers():
    routers = []

    for prefix, version_routes in routes.items():
        router = APIRouter(
            prefix=f"/{prefix}",
            tags=[prefix],
        )
        for route in version_routes:
            router.include_router(route)
        routers.append(router)
    
    return routers

print(get_api_routers())