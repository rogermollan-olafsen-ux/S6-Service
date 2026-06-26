"""Inbox: aggregated notifications from every service.

This is an aggregation layer — it stores lightweight items that point at the
owning service via `target`, not copies of that service's data. Other routers
call `notify(...)` to drop an item in the inbox.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from visma_hq_api.db import get_session
from visma_hq_api.dependencies import get_current_employee
from visma_hq_api.models import Employee, Notification
from visma_hq_api.schemas import NotificationRead

router = APIRouter()


async def notify(
    session: AsyncSession,
    *,
    employee_id: int,
    source: str,
    title: str,
    body: str = "",
    category: str = "info",
    target: str = "",
) -> Notification:
    """Add an inbox item. Caller is responsible for committing the session."""
    item = Notification(
        employee_id=employee_id,
        source=source,
        category=category,
        title=title,
        body=body,
        target=target,
    )
    session.add(item)
    return item


@router.get("", response_model=list[NotificationRead])
async def list_notifications(
    category: str | None = None,
    session: AsyncSession = Depends(get_session),
    employee: Employee = Depends(get_current_employee),
) -> list[Notification]:
    stmt = (
        select(Notification)
        .where(Notification.employee_id == employee.id)
        .order_by(Notification.created_at.desc())
    )
    if category:
        stmt = stmt.where(Notification.category == category)
    rows = await session.scalars(stmt)
    return list(rows)


@router.post("/{notification_id}/read", response_model=NotificationRead)
async def mark_read(
    notification_id: int,
    session: AsyncSession = Depends(get_session),
    employee: Employee = Depends(get_current_employee),
) -> Notification:
    item = await session.get(Notification, notification_id)
    if item is None or item.employee_id != employee.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    if item.read_at is None:
        item.read_at = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(item)
    return item


@router.post("/read-all")
async def mark_all_read(
    session: AsyncSession = Depends(get_session),
    employee: Employee = Depends(get_current_employee),
) -> dict[str, str]:
    await session.execute(
        update(Notification)
        .where(Notification.employee_id == employee.id, Notification.read_at.is_(None))
        .values(read_at=datetime.now(timezone.utc))
    )
    await session.commit()
    return {"status": "ok"}
