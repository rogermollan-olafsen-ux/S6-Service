"""End-to-end API tests against a seeded in-memory database."""

from __future__ import annotations

from httpx import AsyncClient


async def test_health(client: AsyncClient) -> None:
    r = await client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


async def test_me(client: AsyncClient) -> None:
    r = await client.get("/api/me")
    assert r.status_code == 200
    assert r.json()["email"] == "roger.mollan-olafsen@visma.com"


async def test_wallet_balance_and_pay(client: AsyncClient) -> None:
    r = await client.get("/api/wallet")
    assert r.status_code == 200
    assert r.json()["balance_ore"] == 24800

    r = await client.post("/api/wallet/pay", json={"merchant": "Barista Bar", "amount_ore": 3900})
    assert r.status_code == 200
    assert r.json()["balance_ore"] == 24800 - 3900

    # transaction recorded
    r = await client.get("/api/wallet/transactions")
    assert r.status_code == 200
    assert any(t["merchant"] == "Barista Bar" and t["amount_ore"] == -3900 for t in r.json())


async def test_pay_insufficient_balance(client: AsyncClient) -> None:
    r = await client.post("/api/wallet/pay", json={"merchant": "Big spend", "amount_ore": 9_999_999})
    assert r.status_code == 400


async def test_topup(client: AsyncClient) -> None:
    r = await client.post("/api/wallet/topup", json={"amount_ore": 10000})
    assert r.status_code == 200
    assert r.json()["balance_ore"] == 24800 + 10000


async def test_locker_toggle(client: AsyncClient) -> None:
    r = await client.get("/api/lockers/mine")
    assert r.status_code == 200
    lockers = r.json()
    assert len(lockers) == 1
    locker = lockers[0]
    assert locker["code"] == "B-114"
    assert locker["state"] == "locked"

    r = await client.post(f"/api/lockers/{locker['id']}/toggle")
    assert r.status_code == 200
    assert r.json()["state"] == "unlocked"


async def test_massage_book_and_conflict(client: AsyncClient) -> None:
    r = await client.get("/api/massage/slots")
    assert r.status_code == 200
    free = [s for s in r.json() if s["status"] == "free"]
    assert free
    slot_id = free[0]["id"]

    r = await client.post(f"/api/massage/slots/{slot_id}/book")
    assert r.status_code == 200
    assert r.json()["status"] == "booked"

    # double-booking the same slot conflicts
    r = await client.post(f"/api/massage/slots/{slot_id}/book")
    assert r.status_code == 409


async def test_reserve_desk(client: AsyncClient) -> None:
    r = await client.get("/api/spaces?kind=desk")
    assert r.status_code == 200
    free = [s for s in r.json() if s["status"] == "free"]
    assert free
    space_id = free[0]["id"]

    r = await client.post(f"/api/spaces/{space_id}/reserve")
    assert r.status_code == 200
    assert r.json()["status"] == "reserved"


async def test_me_includes_profile_fields(client: AsyncClient) -> None:
    r = await client.get("/api/me")
    assert r.status_code == 200
    data = r.json()
    assert data["employee_no"] == "100482"
    assert data["department"] == "Design & Research"
    assert data["allergies"]  # seeded


async def test_patch_profile_only_editable_fields(client: AsyncClient) -> None:
    r = await client.patch("/api/me", json={"allergies": "Gluten", "emergency_contact": "Test 999 99 999"})
    assert r.status_code == 200
    data = r.json()
    assert data["allergies"] == "Gluten"
    assert data["emergency_contact"] == "Test 999 99 999"
    # read-only Org Master field unchanged
    assert data["department"] == "Design & Research"


async def test_packages_list_and_collect(client: AsyncClient) -> None:
    r = await client.get("/api/packages/mine")
    assert r.status_code == 200
    pkgs = r.json()
    assert any(p["status"] == "arrived" for p in pkgs)
    pending = next(p for p in pkgs if p["status"] == "arrived")

    r = await client.post(f"/api/packages/{pending['id']}/collect")
    assert r.status_code == 200
    assert r.json()["status"] == "collected"

    # collecting again conflicts
    r = await client.post(f"/api/packages/{pending['id']}/collect")
    assert r.status_code == 409


async def test_notifications_and_mark_read(client: AsyncClient) -> None:
    r = await client.get("/api/notifications")
    assert r.status_code == 200
    items = r.json()
    assert items
    unread = [n for n in items if n["read_at"] is None]
    assert unread

    nid = unread[0]["id"]
    r = await client.post(f"/api/notifications/{nid}/read")
    assert r.status_code == 200
    assert r.json()["read_at"] is not None

    # filter by category
    r = await client.get("/api/notifications?category=action")
    assert r.status_code == 200
    assert all(n["category"] == "action" for n in r.json())


async def test_mark_all_read(client: AsyncClient) -> None:
    r = await client.post("/api/notifications/read-all")
    assert r.status_code == 200
    r = await client.get("/api/notifications")
    assert all(n["read_at"] is not None for n in r.json())
