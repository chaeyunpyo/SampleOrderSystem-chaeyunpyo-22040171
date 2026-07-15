from __future__ import annotations

from pathlib import Path

from sample_order_system.model.json_store import load_json, save_json_atomic
from sample_order_system.model.production_queue import ProductionQueueItem

DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "production_state.json"


class ProductionStateRepository:
    def __init__(self, data_path: Path = DEFAULT_DATA_PATH) -> None:
        self.data_path = data_path

    def load(self) -> tuple[list[ProductionQueueItem], ProductionQueueItem | None]:
        raw = load_json(self.data_path, default={"queue": [], "active": None})
        queue = [ProductionQueueItem.from_dict(item) for item in raw.get("queue", [])]
        active_raw = raw.get("active")
        active = ProductionQueueItem.from_dict(active_raw) if active_raw else None
        return queue, active

    def save(self, queue: list[ProductionQueueItem], active: ProductionQueueItem | None) -> None:
        data = {
            "queue": [item.to_dict() for item in queue],
            "active": active.to_dict() if active else None,
        }
        save_json_atomic(self.data_path, data)
