from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime

from dependencies import get_session
from services.auth import get_current_user
from services.subscriptions_service import SubscriptionService
from .schemas.subscriptions_schemas import SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse
from models.subscriptions import Subscription, SubscriptionStatus
from models.users import User

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

@router.post("/", response_model=SubscriptionResponse)
async def create_subscription(
    subscription: SubscriptionCreate, 
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # Только администратор может создавать подписки напрямую
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Только администратор может выполнять эту операцию")
        
    subscription_service = SubscriptionService(session)
    return await subscription_service.create_subscription(
        customer_id=subscription.customer_id,
        plan_id=subscription.plan_id,
        invoice_id=subscription.invoice_id,
        starts_at=subscription.starts_at,
        ends_at=subscription.ends_at,
        status=subscription.status
    )

@router.get("/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_id: str, 
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    subscription_service = SubscriptionService(session)
    subscription = await subscription_service.get_subscription(subscription_id)
    
    # Проверяем права доступа: пользователь может видеть только свои подписки, админ - любые
    if str(subscription.customer_id) != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="У вас нет доступа к этой подписке")
        
    return subscription

@router.get("/user/{customer_id}", response_model=List[SubscriptionResponse])
async def get_user_subscriptions(
    customer_id: str, 
    active_only: bool = False, 
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # Проверяем права доступа: пользователь может видеть только свои подписки, админ - любые
    if str(customer_id) != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="У вас нет доступа к подпискам этого пользователя")
        
    subscription_service = SubscriptionService(session)
    return await subscription_service.get_user_subscriptions(customer_id, active_only)

@router.get("/plan/{plan_id}", response_model=List[SubscriptionResponse])
async def get_plan_subscriptions(
    plan_id: str, 
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # Только администратор может просматривать все подписки на тариф
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Только администратор может выполнять эту операцию")
        
    subscription_service = SubscriptionService(session)
    return await subscription_service.get_plan_subscriptions(plan_id)

@router.put("/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: str, 
    subscription_data: SubscriptionUpdate, 
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # Только администратор может обновлять подписки
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Только администратор может выполнять эту операцию")
        
    subscription_service = SubscriptionService(session)
    return await subscription_service.update_subscription(
        subscription_id,
        **subscription_data.dict(exclude_unset=True)
    )

@router.delete("/{subscription_id}")
async def delete_subscription(
    subscription_id: str, 
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # Только администратор может удалять подписки
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Только администратор может выполнять эту операцию")
        
    subscription_service = SubscriptionService(session)
    return await subscription_service.delete_subscription(subscription_id)

@router.post("/{subscription_id}/activate", response_model=SubscriptionResponse)
async def activate_subscription(
    subscription_id: str, 
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # Только администратор может активировать подписки
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Только администратор может выполнять эту операцию")
        
    subscription_service = SubscriptionService(session)
    return await subscription_service.activate_subscription(subscription_id)

@router.post("/{subscription_id}/renew", response_model=SubscriptionResponse)
async def renew_subscription(
    subscription_id: str, 
    new_subscription_id: str, 
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # Только администратор может обновлять подписки
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Только администратор может выполнять эту операцию")
        
    subscription_service = SubscriptionService(session)
    return await subscription_service.renew_subscription(subscription_id, new_subscription_id)

@router.post("/{subscription_id}/upgrade", response_model=SubscriptionResponse)
async def upgrade_subscription(
    subscription_id: str, 
    new_plan_id: str, 
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # Только администратор может обновлять подписки
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Только администратор может выполнять эту операцию")
        
    subscription_service = SubscriptionService(session)
    return await subscription_service.upgrade_subscription(subscription_id, new_plan_id)

@router.post("/{subscription_id}/downgrade", response_model=SubscriptionResponse)
async def downgrade_subscription(
    subscription_id: str, 
    new_plan_id: str, 
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # Только администратор может обновлять подписки
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Только администратор может выполнять эту операцию")
        
    subscription_service = SubscriptionService(session)
    return await subscription_service.downgrade_subscription(subscription_id, new_plan_id)

@router.post("/{subscription_id}/cancel", response_model=SubscriptionResponse)
async def cancel_subscription(
    subscription_id: str, 
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    subscription_service = SubscriptionService(session)
    subscription = await subscription_service.get_subscription(subscription_id)
    
    # Проверяем права доступа: пользователь может отменять только свои подписки, админ - любые
    if str(subscription.customer_id) != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="У вас нет доступа к этой подписке")
        
    return await subscription_service.cancel_subscription(subscription_id)

@router.get("/active/user/{customer_id}", response_model=SubscriptionResponse)
async def get_active_subscription_for_user(
    customer_id: str, 
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # Проверяем права доступа: пользователь может видеть только свои подписки, админ - любые
    if str(customer_id) != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="У вас нет доступа к подпискам этого пользователя")
        
    subscription_service = SubscriptionService(session)
    subscription = await subscription_service.get_active_subscription_for_user(customer_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Активная подписка не найдена для пользователя")
    return subscription