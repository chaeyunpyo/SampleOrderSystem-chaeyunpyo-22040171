from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class Sample:
    sample_id: str
    name: str
    avg_production_time: float
    yield_rate: float
    stock_quantity: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Sample":
        return cls(
            sample_id=data["sample_id"],
            name=data["name"],
            avg_production_time=data["avg_production_time"],
            yield_rate=data["yield_rate"],
            stock_quantity=data.get("stock_quantity", 0),
        )
