from __future__ import annotations

import pytest

import ws_bridge


class DummyClient:
    def __init__(self, closed: bool = False):
        self.closed = closed
        self.sent = 0

    async def send_json(self, message):
        self.sent += 1
        return None


@pytest.mark.asyncio
async def test_broadcast_skips_closed_clients(monkeypatch):
    c1 = DummyClient(closed=False)
    c2 = DummyClient(closed=True)
    c3 = DummyClient(closed=False)

    monkeypatch.setattr(ws_bridge, "connected_clients", {c1, c2, c3})
    await ws_bridge.broadcast_to_clients({"type": "x"})

    assert c1.sent == 1
    assert c2.sent == 0
    assert c3.sent == 1
