"""Seed the database with demo data on startup (idempotent)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from visma_hq_api.models import (
    Employee,
    Locker,
    MassageSlot,
    Space,
    Transaction,
    Wallet,
)


async def seed(session: AsyncSession) -> None:
    existing = await session.scalar(select(Employee).limit(1))
    if existing is not None:
        return  # already seeded

    roger = Employee(
        id=1, name="Roger", email="roger.mollan-olafsen@visma.com", floor=6
    )
    session.add(roger)

    wallet = Wallet(employee=roger, balance_ore=24800)
    session.add(wallet)
    session.add_all(
        [
            Transaction(wallet=wallet, merchant="Barista Bar", amount_ore=-3900, kind="payment"),
            Transaction(wallet=wallet, merchant="Cafeteria lunch", amount_ore=-8900, kind="payment"),
            Transaction(wallet=wallet, merchant="Top-up · Visa ••42", amount_ore=30000, kind="topup"),
        ]
    )

    session.add_all(
        [
            Locker(code="B-112", floor=6, wing="B", state="locked"),
            Locker(code="B-114", floor=6, wing="B", assigned_employee_id=1, state="locked"),
        ]
    )

    session.add_all(
        [
            MassageSlot(day="Today", start_time="10:00", kind="Relax", status="booked"),
            MassageSlot(day="Today", start_time="13:00", kind="Deep tissue"),
            MassageSlot(day="Today", start_time="13:30", kind="Relax"),
            MassageSlot(day="Today", start_time="15:00", kind="Deep tissue"),
        ]
    )

    session.add_all(
        [
            Space(name="Desk 6-22", kind="desk", capacity=1, zone="Window"),
            Space(name="Desk 6-30", kind="desk", capacity=1, zone="Quiet zone"),
            Space(name="Desk 6-14", kind="desk", capacity=1, zone="", status="reserved"),
            Space(name='Room "Fjord"', kind="room", capacity=6, zone="Screen · whiteboard"),
            Space(name="Phone booth 3", kind="booth", capacity=1, zone="Soundproof"),
        ]
    )

    await session.commit()
