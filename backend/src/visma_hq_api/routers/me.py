"""Current employee."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from visma_hq_api.db import get_session
from visma_hq_api.dependencies import get_current_employee
from visma_hq_api.models import Employee
from visma_hq_api.schemas import EmployeeRead, ProfileUpdate

router = APIRouter()


@router.get("", response_model=EmployeeRead)
async def read_me(employee: Employee = Depends(get_current_employee)) -> Employee:
    return employee


@router.patch("", response_model=EmployeeRead)
async def update_me(
    payload: ProfileUpdate,
    session: AsyncSession = Depends(get_session),
    employee: Employee = Depends(get_current_employee),
) -> Employee:
    """Update only the employee-owned fields. Org Master data stays read-only."""
    if payload.emergency_contact is not None:
        employee.emergency_contact = payload.emergency_contact
    if payload.allergies is not None:
        employee.allergies = payload.allergies
    await session.commit()
    await session.refresh(employee)
    return employee
