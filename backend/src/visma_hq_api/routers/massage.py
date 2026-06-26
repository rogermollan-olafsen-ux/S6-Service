"""In-house massage: list slots, book, cancel."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from visma_hq_api.db import get_session
from visma_hq_api.dependencies import get_current_employee
from visma_hq_api.models import Employee, MassageSlot
from visma_hq_api.schemas import MassageSlotRead

router = APIRouter()


@router.get("/slots", response_model=list[MassageSlotRead])
async def list_slots(
    day: str | None = None,
    session: AsyncSession = Depends(get_session),
) -> list[MassageSlot]:
    stmt = select(MassageSlot).order_by(MassageSlot.start_time)
    if day:
        stmt = stmt.where(MassageSlot.day == day)
    rows = await session.scalars(stmt)
    return list(rows)


@router.post("/slots/{slot_id}/book", response_model=MassageSlotRead)
async def book_slot(
    slot_id: int,
    session: AsyncSession = Depends(get_session),
    employee: Employee = Depends(get_current_employee),
) -> MassageSlot:
    slot = await session.get(MassageSlot, slot_id)
    if slot is None:
        raise HTTPException(status_code=404, detail="Slot not found")
    if slot.status == "booked":
        raise HTTPException(status_code=409, detail="Slot already booked")
    slot.status = "booked"
    slot.booked_by_id = employee.id
    await session.commit()
    await session.refresh(slot)
    return slot


@router.delete("/slots/{slot_id}/book", response_model=MassageSlotRead)
async def cancel_slot(
    slot_id: int,
    session: AsyncSession = Depends(get_session),
    employee: Employee = Depends(get_current_employee),
) -> MassageSlot:
    slot = await session.get(MassageSlot, slot_id)
    if slot is None:
        raise HTTPException(status_code=404, detail="Slot not found")
    if slot.booked_by_id != employee.id:
        raise HTTPException(status_code=403, detail="Not your booking")
    slot.status = "free"
    slot.booked_by_id = None
    await session.commit()
    await session.refresh(slot)
    return slot
