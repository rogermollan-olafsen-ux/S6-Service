"""Shared FastAPI dependencies."""

from __future__ import annotations

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from visma_hq_api.db import get_session
from visma_hq_api.models import Employee

# Demo employee id. In a real build this is resolved from a Visma SSO token
# (OIDC) instead of being hard-coded — see README "Open questions".
DEMO_EMPLOYEE_ID = 1


async def get_current_employee(
    session: AsyncSession = Depends(get_session),
) -> Employee:
    """Return the signed-in employee. STUB: always the seeded demo user."""
    employee = await session.get(Employee, DEMO_EMPLOYEE_ID)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


__all__ = ["get_current_employee", "get_session", "select", "AsyncSession"]
