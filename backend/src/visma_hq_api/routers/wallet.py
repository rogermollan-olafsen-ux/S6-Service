"""HQ wallet: balance, transactions, pay, top-up."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from visma_hq_api.db import get_session
from visma_hq_api.dependencies import get_current_employee
from visma_hq_api.models import Employee, Transaction, Wallet
from visma_hq_api.schemas import (
    PayRequest,
    TopUpRequest,
    TransactionRead,
    WalletRead,
)

router = APIRouter()


async def _wallet_for(session: AsyncSession, employee: Employee) -> Wallet:
    wallet = await session.scalar(
        select(Wallet).where(Wallet.employee_id == employee.id)
    )
    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet


@router.get("", response_model=WalletRead)
async def get_wallet(
    session: AsyncSession = Depends(get_session),
    employee: Employee = Depends(get_current_employee),
) -> WalletRead:
    wallet = await _wallet_for(session, employee)
    return WalletRead(balance_ore=wallet.balance_ore, floor=employee.floor)


@router.get("/transactions", response_model=list[TransactionRead])
async def list_transactions(
    session: AsyncSession = Depends(get_session),
    employee: Employee = Depends(get_current_employee),
) -> list[Transaction]:
    wallet = await _wallet_for(session, employee)
    rows = await session.scalars(
        select(Transaction)
        .where(Transaction.wallet_id == wallet.id)
        .order_by(Transaction.created_at.desc())
    )
    return list(rows)


@router.post("/pay", response_model=WalletRead)
async def pay(
    payload: PayRequest,
    session: AsyncSession = Depends(get_session),
    employee: Employee = Depends(get_current_employee),
) -> WalletRead:
    wallet = await _wallet_for(session, employee)
    if payload.amount_ore > wallet.balance_ore:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    wallet.balance_ore -= payload.amount_ore
    session.add(
        Transaction(
            wallet_id=wallet.id,
            merchant=payload.merchant,
            amount_ore=-payload.amount_ore,
            kind="payment",
        )
    )
    await session.commit()
    return WalletRead(balance_ore=wallet.balance_ore, floor=employee.floor)


@router.post("/topup", response_model=WalletRead)
async def topup(
    payload: TopUpRequest,
    session: AsyncSession = Depends(get_session),
    employee: Employee = Depends(get_current_employee),
) -> WalletRead:
    wallet = await _wallet_for(session, employee)
    wallet.balance_ore += payload.amount_ore
    session.add(
        Transaction(
            wallet_id=wallet.id,
            merchant="Top-up · Visa ••42",
            amount_ore=payload.amount_ore,
            kind="topup",
        )
    )
    await session.commit()
    return WalletRead(balance_ore=wallet.balance_ore, floor=employee.floor)
