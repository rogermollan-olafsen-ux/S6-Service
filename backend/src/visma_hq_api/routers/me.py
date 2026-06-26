"""Current employee."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from visma_hq_api.dependencies import get_current_employee
from visma_hq_api.models import Employee
from visma_hq_api.schemas import EmployeeRead

router = APIRouter()


@router.get("", response_model=EmployeeRead)
async def read_me(employee: Employee = Depends(get_current_employee)) -> Employee:
    return employee
