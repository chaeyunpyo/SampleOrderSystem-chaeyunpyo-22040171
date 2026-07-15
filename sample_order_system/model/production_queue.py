from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProductionQueueItem:
    order_id: str
    sample_id: str
    shortage_qty: int
    avg_production_time: float
    yield_rate: float
    enqueued_at: datetime | None = None
    started_at: datetime | None = None
    actual_production_qty: int | None = None
    total_production_time: float | None = None

    def __post_init__(self) -> None:
        if self.enqueued_at is None:
            self.enqueued_at = datetime.now()
        if self.actual_production_qty is None:
            self.actual_production_qty = math.ceil(self.shortage_qty / self.yield_rate)
        if self.total_production_time is None:
            self.total_production_time = self.avg_production_time * self.actual_production_qty

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "sample_id": self.sample_id,
            "shortage_qty": self.shortage_qty,
            "avg_production_time": self.avg_production_time,
            "yield_rate": self.yield_rate,
            "enqueued_at": self.enqueued_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "actual_production_qty": self.actual_production_qty,
            "total_production_time": self.total_production_time,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProductionQueueItem":
        return cls(
            order_id=data["order_id"],
            sample_id=data["sample_id"],
            shortage_qty=data["shortage_qty"],
            avg_production_time=data["avg_production_time"],
            yield_rate=data["yield_rate"],
            enqueued_at=datetime.fromisoformat(data["enqueued_at"]),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            actual_production_qty=data["actual_production_qty"],
            total_production_time=data["total_production_time"],
        )
