from __future__ import annotations

from pathlib import Path

from sample_order_system.model.json_store import load_json, next_prefixed_id, save_json_atomic
from sample_order_system.model.order import Order

DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "orders.json"


class OrderNotFoundError(Exception):
    pass


class OrderRepository:
    def __init__(self, data_path: Path = DEFAULT_DATA_PATH) -> None:
        self.data_path = data_path
        self._orders: dict[str, Order] = {}
        self._load()

    def _load(self) -> None:
        raw = load_json(self.data_path, default=[])
        self._orders = {item["order_id"]: Order.from_dict(item) for item in raw}

    def _save(self) -> None:
        save_json_atomic(self.data_path, [order.to_dict() for order in self._orders.values()])

    def next_id(self) -> str:
        return next_prefixed_id(list(self._orders.keys()), prefix="O")

    def create(self, order: Order) -> Order:
        self._orders[order.order_id] = order
        self._save()
        return order

    def get(self, order_id: str) -> Order:
        try:
            return self._orders[order_id]
        except KeyError:
            raise OrderNotFoundError(f"존재하지 않는 주문입니다: {order_id}") from None

    def list_all(self) -> list[Order]:
        return list(self._orders.values())

    def save(self, order: Order) -> Order:
        self._orders[order.order_id] = order
        self._save()
        return order
