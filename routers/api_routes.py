from fastapi import APIRouter

from .api_v1 import  users, subscription_plans, subscriptions, payments, auth, registration, yookassa_payments, webhooks

routes = {
    'api_v1' : [
        users.router,
        subscription_plans.router,
        subscriptions.router,
        payments.router,
        auth.router,
        registration.router,
        yookassa_payments.router,
        webhooks.router,
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