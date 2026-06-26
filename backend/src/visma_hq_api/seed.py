"""Seed the database with demo data on startup (idempotent)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from visma_hq_api.models import (
    Employee,
    Locker,
    MassageSlot,
    Notification,
    Package,
    Space,
    Transaction,
    Wallet,
)


async def seed(session: AsyncSession) -> None:
    existing = await session.scalar(select(Employee).limit(1))
    if existing is not None:
        return  # already seeded

    roger = Employee(
        id=1,
        name="Roger Mollan-Olafsen",
        email="roger.mollan-olafsen@visma.com",
        floor=6,
        employee_no="100482",
        title="UX Designer",
        department="Design & Research",
        manager="Kari Nordmann",
        emergency_contact="Mari M-O · 412 33 221",
        allergies="Nuts, lactose",
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

    session.add_all(
        [
            Package(
                recipient_id=1, description="PostNord parcel", carrier="PostNord",
                location_type="locker", locker_code="4192", status="arrived",
            ),
            Package(
                recipient_id=1, description="Letter · signed for", carrier="Posten",
                location_type="reception", pickup_code="R-100482", status="arrived",
            ),
            Package(
                recipient_id=1, description="Amazon parcel", carrier="Amazon",
                location_type="locker", locker_code="0098", status="collected",
            ),
        ]
    )

    session.add_all(
        [
            Notification(
                employee_id=1, source="packages", category="action",
                title="Parcel ready to collect",
                body="PostNord parcel in smart locker P-07. Code 4192.",
                target="pakker",
            ),
            Notification(
                employee_id=1, source="wellness", category="action",
                title="Massage reminder",
                body="Your session is today at 13:00 in the wellness room.",
                target="massage",
            ),
            Notification(
                employee_id=1, source="pay", category="info",
                title="Payment receipt", body="kr 39,00 at Barista Bar.",
                target="pay",
                read_at=datetime(2026, 6, 26, 6, 32, tzinfo=timezone.utc),
            ),
        ]
    )

    await session.commit()
