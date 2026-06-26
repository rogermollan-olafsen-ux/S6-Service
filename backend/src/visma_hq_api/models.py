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
