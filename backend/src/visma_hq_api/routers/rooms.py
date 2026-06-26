"""Rooms & desks: list spaces, reserve, release."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from visma_hq_api.db import get_session
from visma_hq_api.dependencies import get_current_employee
from visma_hq_api.models import Employee, Space
from visma_hq_api.schemas import SpaceRead

router = APIRouter()


@router.get("", response_model=list[SpaceRead])
async def list_spaces(
    kind: str | None = None,
    session: AsyncSession = Depends(get_session),
) -> list[Space]:
    stmt = select(Space).order_by(Space.name)
    if kind:
        stmt = stmt.where(Space.kind == kind)
    rows = await session.scalars(stmt)
    return list(rows)


@router.post("/{space_id}/reserve", response_model=SpaceRead)
async def reserve_space(
    space_id: int,
    session: AsyncSession = Depends(get_session),
    employee: Employee = Depends(get_current_employee),
) -> Space:
    space = await session.get(Space, space_id)
    if space is None:
        raise HTTPException(status_code=404, detail="Space not found")
    if space.status == "reserved":
        raise HTTPException(status_code=409, detail="Space already reserved")
    space.status = "reserved"
    space.reserved_by_id = employee.id
    await session.commit()
    await session.refresh(space)
    return space


@router.post("/{space_id}/release", response_model=SpaceRead)
async def release_space(
    space_id: int,
    session: AsyncSession = Depends(get_session),
    employee: Employee = Depends(get_current_employee),
) -> Space:
    space = await session.get(Space, space_id)
    if space is None:
        raise HTTPException(status_code=404, detail="Space not found")
    if space.reserved_by_id != employee.id:
        raise HTTPException(status_code=403, detail="Not your reservation")
    space.status = "free"
    space.reserved_by_id = None
    await session.commit()
    await session.refresh(space)
    return space
