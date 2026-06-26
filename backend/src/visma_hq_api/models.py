"""SQLAlchemy ORM models.

Monetary values are stored as integer øre (1 NOK = 100 øre) to avoid floats.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from visma_hq_api.db import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(200), unique=True)
    floor: Mapped[int] = mapped_column(default=6)

    # Mirrored read-only from Visma Organisation Master (source of truth).
    employee_no: Mapped[str] = mapped_column(String(20), default="")
    title: Mapped[str] = mapped_column(String(120), default="")
    department: Mapped[str] = mapped_column(String(120), default="")
    manager: Mapped[str] = mapped_column(String(120), default="")

    # Owned by the employee, editable in the app.
    emergency_contact: Mapped[str] = mapped_column(String(200), default="")
    allergies: Mapped[str] = mapped_column(String(200), default="")

    wallet: Mapped["Wallet"] = relationship(back_populates="employee", uselist=False)


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    balance_ore: Mapped[int] = mapped_column(default=0)

    employee: Mapped[Employee] = relationship(back_populates="wallet")
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="wallet", order_by="Transaction.created_at.desc()"
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id"))
    merchant: Mapped[str] = mapped_column(String(120))
    # negative = spend, positive = top-up
    amount_ore: Mapped[int] = mapped_column()
    kind: Mapped[str] = mapped_column(String(20))  # "payment" | "topup"
    created_at: Mapped[datetime] = mapped_column(default=_now)

    wallet: Mapped[Wallet] = relationship(back_populates="transactions")


class Locker(Base):
    __tablename__ = "lockers"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True)  # e.g. "B-114"
    floor: Mapped[int] = mapped_column(default=6)
    wing: Mapped[str] = mapped_column(String(20), default="B")
    assigned_employee_id: Mapped[int | None] = mapped_column(
        ForeignKey("employees.id"), nullable=True
    )
    state: Mapped[str] = mapped_column(String(20), default="locked")  # locked|unlocked


class MassageSlot(Base):
    __tablename__ = "massage_slots"

    id: Mapped[int] = mapped_column(primary_key=True)
    day: Mapped[str] = mapped_column(String(20))  # label, e.g. "Today", "Thu 27"
    start_time: Mapped[str] = mapped_column(String(10))  # "13:00"
    duration_min: Mapped[int] = mapped_column(default=25)
    therapist: Mapped[str] = mapped_column(String(80), default="Anna")
    kind: Mapped[str] = mapped_column(String(40), default="Deep tissue")
    status: Mapped[str] = mapped_column(String(20), default="free")  # free|booked
    booked_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("employees.id"), nullable=True
    )


class Space(Base):
    __tablename__ = "spaces"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))  # "Desk 6-22", 'Room "Fjord"'
    kind: Mapped[str] = mapped_column(String(20))  # desk|room|booth
    floor: Mapped[int] = mapped_column(default=6)
    capacity: Mapped[int] = mapped_column(default=1)
    zone: Mapped[str] = mapped_column(String(80), default="")
    status: Mapped[str] = mapped_column(String(20), default="free")  # free|reserved
    reserved_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("employees.id"), nullable=True
    )


class Package(Base):
    __tablename__ = "packages"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipient_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    description: Mapped[str] = mapped_column(String(120))
    carrier: Mapped[str] = mapped_column(String(60), default="")
    # Where to collect it: a smart locker (with a code) or the staffed reception.
    location_type: Mapped[str] = mapped_column(String(20), default="locker")  # locker|reception
    locker_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    pickup_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="arrived")  # arrived|collected
    arrived_at: Mapped[datetime] = mapped_column(default=_now)
    collected_at: Mapped[datetime | None] = mapped_column(nullable=True)


class Notification(Base):
    """Lightweight aggregated inbox item. Points at a service; does not own data."""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    source: Mapped[str] = mapped_column(String(40))  # packages|wellness|pay|lockers|rooms
    category: Mapped[str] = mapped_column(String(20), default="info")  # action|info
    title: Mapped[str] = mapped_column(String(120))
    body: Mapped[str] = mapped_column(String(300), default="")
    target: Mapped[str] = mapped_column(String(40), default="")  # deep-link screen id
    created_at: Mapped[datetime] = mapped_column(default=_now)
    read_at: Mapped[datetime | None] = mapped_column(nullable=True)
