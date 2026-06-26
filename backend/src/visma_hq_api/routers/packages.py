"""Incoming packages: list parcels, mark collected."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from visma_hq_api.db import get_session
from visma_hq_api.dependencies import get_current_employee
from visma_hq_api.models import Employee, Package
from visma_hq_api.schemas import PackageRead

router = APIRouter()


@router.get("/mine", response_model=list[PackageRead])
async def my_packages(
    session: AsyncSession = Depends(get_session),
    employee: Employee = Depends(get_current_employee),
) -> list[Package]:
    rows = await session.scalars(
        select(Package)
        .where(Package.recipient_id == employee.id)
        .order_by(Package.arrived_at.desc())
    )
    return list(rows)


@router.post("/{package_id}/collect", response_model=PackageRead)
async def collect_package(
    package_id: int,
    session: AsyncSession = Depends(get_session),
    employee: Employee = Depends(get_current_employee),
) -> Package:
    pkg = await session.get(Package, package_id)
    if pkg is None or pkg.recipient_id != employee.id:
        raise HTTPException(status_code=404, detail="Package not found")
    if pkg.status == "collected":
        raise HTTPException(status_code=409, detail="Already collected")
    pkg.status = "collected"
    pkg.collected_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(pkg)
    return pkg
