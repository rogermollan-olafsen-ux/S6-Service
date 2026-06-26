"""Pydantic v2 response/request schemas (the public API contract)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class EmployeeRead(ORMModel):
    id: int
    name: str
    email: str
    floor: int
    employee_no: str
    title: str
    department: str
    manager: str
    emergency_contact: str
    allergies: str


class ProfileUpdate(BaseModel):
    """Only the employee-owned fields are editable; Org Master data is read-only."""

    emergency_contact: str | None = Field(default=None, max_length=200)
    allergies: str | None = Field(default=None, max_length=200)


class WalletRead(ORMModel):
    balance_ore: int
    floor: int = 6
    location: str = "Oslo HQ"


class TransactionRead(ORMModel):
    id: int
    merchant: str
    amount_ore: int
    kind: str
    created_at: datetime


class PayRequest(BaseModel):
    merchant: str = Field(min_length=1, max_length=120)
    amount_ore: int = Field(gt=0, description="Amount to charge, in øre")


class TopUpRequest(BaseModel):
    amount_ore: int = Field(gt=0, description="Amount to add, in øre")


class LockerRead(ORMModel):
    id: int
    code: str
    floor: int
    wing: str
    state: str


class MassageSlotRead(ORMModel):
    id: int
    day: str
    start_time: str
    duration_min: int
    therapist: str
    kind: str
    status: str


class SpaceRead(ORMModel):
    id: int
    name: str
    kind: str
    floor: int
    capacity: int
    zone: str
    status: str


class PackageRead(ORMModel):
    id: int
    description: str
    carrier: str
    location_type: str
    locker_code: str | None
    pickup_code: str | None
    status: str
    arrived_at: datetime
    collected_at: datetime | None


class NotificationRead(ORMModel):
    id: int
    source: str
    category: str
    title: str
    body: str
    target: str
    created_at: datetime
    read_at: datetime | None
