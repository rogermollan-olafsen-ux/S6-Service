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
