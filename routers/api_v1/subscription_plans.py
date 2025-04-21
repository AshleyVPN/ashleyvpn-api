import dependencies
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from dependencies import get_session

from services.auth import get_current_user
from services.subscription_plans_service import SubscriptionPlanService
from .schemas.subscription_plans_schemas import SubscriptionPlanCreate, SubscriptionPlanUpdate, QuotaCreate, PriceCreate, SubscriptionPlanResponse, QuotaResponse, PriceResponse
from models.subscription_plans import ResourceType
from models.users import User

router = APIRouter(prefix="/subscription-plans", tags=["subscription-plans"])

@router.post("/", response_model=SubscriptionPlanResponse)
async def create_subscription_plan(
    plan: SubscriptionPlanCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Только администратор может создавать тарифные планы
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Только администратор может выполнять эту операцию")
        
    plan_service = SubscriptionPlanService(db)
    subscription_plan = await plan_service.create_subscription_plan(
        name=plan.name,
        description=plan.description,
        billing_interval=plan.billing_interval,
        is_active=plan.is_active,
        has_trial=plan.has_trial,
        trial_discount=plan.trial_discount,
        transfer_plan_id=plan.transfer_plan_id
    )
    
    # Добавление квот, если они указаны
    if plan.quotas:
        for quota in plan.quotas:
            await plan_service.add_quota(
                plan_id=str(subscription_plan.id),
                resource_type=quota.resource_type,
                limit=quota.limit,
                constraints=quota.constraints
            )
    
    # Добавление цен, если они указаны
    if plan.prices:
        for price in plan.prices:
            await plan_service.add_price(
                plan_id=str(subscription_plan.id),
                amount=price.amount,
                currency=price.currency
            )
    
    return subscription_plan

@router.get("/{plan_id}", response_model=SubscriptionPlanResponse)
async def get_subscription_plan(plan_id: str, db: Session = Depends(get_session)):
    # Просмотр тарифов доступен всем пользователям, даже без авторизации
    plan_service = SubscriptionPlanService(db)
    return await plan_service.get_subscription_plan(plan_id)

@router.get("/", response_model=List[SubscriptionPlanResponse])
async def get_all_subscription_plans(active_only: bool = False, db: Session = Depends(get_session)):
    plan_service = SubscriptionPlanService(db)
    return await plan_service.get_all_subscription_plans(active_only)

@router.put("/{plan_id}", response_model=SubscriptionPlanResponse)
async def update_subscription_plan(
    plan_id: str, 
    plan_data: SubscriptionPlanUpdate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Только администратор может обновлять тарифные планы
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Только администратор может выполнять эту операцию")
        
    plan_service = SubscriptionPlanService(db)
    return await plan_service.update_subscription_plan(
        plan_id,
        **plan_data.dict(exclude_unset=True)
    )

@router.delete("/{plan_id}")
async def delete_subscription_plan(
    plan_id: str, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Только администратор может удалять тарифные планы
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Только администратор может выполнять эту операцию")
        
    plan_service = SubscriptionPlanService(db)
    return await plan_service.delete_subscription_plan(plan_id)

# Эндпоинты для квот
@router.post("/{plan_id}/quotas", response_model=QuotaResponse)
async def add_quota(
    plan_id: str, 
    quota: QuotaCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Только администратор может добавлять квоты к тарифным планам
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Только администратор может выполнять эту операцию")
        
    plan_service = SubscriptionPlanService(db)
    return await plan_service.add_quota(
        plan_id=plan_id,
        resource_type=quota.resource_type,
        limit=quota.limit,
        constraints=quota.constraints
    )

@router.get("/{plan_id}/quotas", response_model=List[QuotaResponse])
async def get_plan_quotas(plan_id: str, db: Session = Depends(get_session)):
    plan_service = SubscriptionPlanService(db)
    return await plan_service.get_plan_quotas(plan_id)

@router.put("/quotas/{quota_id}", response_model=QuotaResponse)
async def update_quota(
    quota_id: str, 
    quota_data: QuotaCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Только администратор может обновлять квоты
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Только администратор может выполнять эту операцию")
        
    plan_service = SubscriptionPlanService(db)
    return await plan_service.update_quota(
        quota_id,
        resource_type=quota_data.resource_type,
        limit=quota_data.limit,
        constraints=quota_data.constraints
    )

@router.delete("/quotas/{quota_id}")
async def delete_quota(
    quota_id: str, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Только администратор может удалять квоты
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Только администратор может выполнять эту операцию")
        
    plan_service = SubscriptionPlanService(db)
    return await plan_service.delete_quota(quota_id)

# Эндпоинты для цен
@router.post("/{plan_id}/prices", response_model=PriceResponse)
async def add_price(plan_id: str, price: PriceCreate, db: Session = Depends(get_session)):
    plan_service = SubscriptionPlanService(db)
    return await plan_service.add_price(
        plan_id=plan_id,
        amount=price.amount,
        currency=price.currency
    )

@router.get("/{plan_id}/prices", response_model=List[PriceResponse])
async def get_plan_prices(plan_id: str, db: Session = Depends(get_session)):
    plan_service = SubscriptionPlanService(db)
    return await plan_service.get_plan_prices(plan_id)

@router.put("/prices/{price_id}", response_model=PriceResponse)
async def update_price(price_id: str, price_data: PriceCreate, db: Session = Depends(get_session)):
    plan_service = SubscriptionPlanService(db)
    return await plan_service.update_price(
        price_id,
        amount=price_data.amount,
        currency=price_data.currency
    )

@router.delete("/prices/{price_id}")
async def delete_price(price_id: str, db: Session = Depends(get_session)):
    plan_service = SubscriptionPlanService(db)
    return await plan_service.delete_price(price_id)