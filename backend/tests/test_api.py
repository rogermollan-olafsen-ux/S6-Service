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
