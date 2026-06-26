"""Personal lockers: view assigned, toggle lock state."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from visma_hq_api.db import get_session
from visma_hq_api.dependencies import get_current_employee
from visma_hq_api.models import Employee, Locker
from visma_hq_api.schemas import LockerRead

router = APIRouter()


@router.get("/mine", response_model=list[LockerRead])
async def my_lockers(
    session: AsyncSession = Depends(get_session),
    employee: Employee = Depends(get_current_employee),
) -> list[Locker]:
    rows = await session.scalars(
        select(Locker).where(Locker.assigned_employee_id == employee.id)
    )
    return list(rows)


@router.post("/{locker_id}/toggle", response_model=LockerRead)
async def toggle_locker(
    locker_id: int,
    session: AsyncSession = Depends(get_session),
    employee: Employee = Depends(get_current_employee),
) -> Locker:
    locker = await session.get(Locker, locker_id)
    if locker is None:
        raise HTTPException(status_code=404, detail="Locker not found")
    if locker.assigned_employee_id != employee.id:
        raise HTTPException(status_code=403, detail="Not your locker")
    locker.state = "unlocked" if locker.state == "locked" else "locked"
    await session.commit()
    await session.refresh(locker)
    return locker
