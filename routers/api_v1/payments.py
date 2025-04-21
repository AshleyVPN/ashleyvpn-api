from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from dependencies import get_session
from services.auth import get_current_user
from services.payments_service import PaymentService
from .schemas.payments_schemas import PaymentCreate, PaymentInput, PaymentResponse, PaymentMethodResponse
from models.users import User

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/", response_model=PaymentResponse)
async def create_payment(
    payment: PaymentCreate, 
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # Проверяем, что пользователь создает платеж для себя
    if payment.user_id != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Вы можете создавать платежи только для своего аккаунта")
        
    payment_service = PaymentService(session)
    return await payment_service.create_payment(
        user_id=payment.user_id,
        amount=float(payment.price),
        currency=payment.currency,
        subscription_plan_id=payment.tarrif_id,
        payment_method=payment.payment_method,
        payment_kassa=payment.payment_method
    )

@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str, 
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    payment_service = PaymentService(session)
    payment = await payment_service.get_payment(payment_id)
    
    # Проверяем, что пользователь запрашивает свой платеж или является администратором
    if payment.user_id != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="У вас нет доступа к этому платежу")
        
    return payment

@router.get("/user/{user_id}", response_model=List[PaymentResponse])
async def get_user_payments(
    user_id: str, 
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # Проверяем, что пользователь запрашивает свои платежи или является администратором
    if user_id != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="У вас нет доступа к платежам этого пользователя")
        
    payment_service = PaymentService(session)
    return await payment_service.get_user_payments(user_id)

@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: str, 
    payment_data: PaymentInput, 
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # Только администратор может обновлять платежи
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Только администратор может выполнять эту операцию")
        
    payment_service = PaymentService(session)
    return await payment_service.update_payment(
        payment_id,
        **payment_data.dict(exclude_unset=True)
    )

@router.delete("/{payment_id}")
async def delete_payment(
    payment_id: str, 
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # Только администратор может удалять платежи
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Только администратор может выполнять эту операцию")
        
    payment_service = PaymentService(session)
    return await payment_service.delete_payment(payment_id)

@router.get("/methods/{user_id}", response_model=List[PaymentMethodResponse])
async def get_user_payment_methods(
    user_id: str, 
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # Проверяем, что пользователь запрашивает свои методы оплаты или является администратором
    if user_id != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="У вас нет доступа к методам оплаты этого пользователя")
        
    payment_service = PaymentService(session)
    return await payment_service.get_user_payment_methods(user_id)

@router.post("/methods", response_model=PaymentMethodResponse)
async def add_payment_method(
    user_id: str,
    method_name: str,
    method_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # Проверяем, что пользователь добавляет метод оплаты для себя или является администратором
    if user_id != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Вы можете добавлять методы оплаты только для своего аккаунта")
        
    payment_service = PaymentService(session)
    return await payment_service.add_payment_method(user_id, method_name, method_id)