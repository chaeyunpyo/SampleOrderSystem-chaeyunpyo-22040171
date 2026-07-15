from __future__ import annotations

from sample_order_system.model.order import OrderStatus
from sample_order_system.model.order_repository import OrderRepository
from sample_order_system.model.sample_repository import SampleRepository

MONITORED_STATUSES = (
    OrderStatus.RESERVED,
    OrderStatus.CONFIRMED,
    OrderStatus.PRODUCING,
    OrderStatus.RELEASE,
)


class MonitoringController:
    def __init__(self, sample_repository: SampleRepository, order_repository: OrderRepository) -> None:
        self.sample_repository = sample_repository
        self.order_repository = order_repository

    def count_by_status(self) -> dict[str, dict[str, int]]:
        result = {status.value: {"count": 0, "quantity": 0} for status in MONITORED_STATUSES}
        for order in self.order_repository.list_all():
            if order.status not in MONITORED_STATUSES:
                continue
            bucket = result[order.status.value]
            bucket["count"] += 1
            bucket["quantity"] += order.quantity
        return result

    def inventory_status(self) -> list[dict]:
        orders = self.order_repository.list_all()
        report = []
        for sample in self.sample_repository.list_all():
            pending_qty = sum(
                o.quantity for o in orders if o.sample_id == sample.sample_id and o.status == OrderStatus.CONFIRMED
            )
            tier = self._inventory_tier(sample.stock_quantity, pending_qty)
            report.append(
                {
                    "sample_id": sample.sample_id,
                    "name": sample.name,
                    "stock_quantity": sample.stock_quantity,
                    "pending_qty": pending_qty,
                    "tier": tier,
                }
            )
        return report

    @staticmethod
    def _inventory_tier(stock_quantity: int, pending_qty: int) -> str:
        if pending_qty == 0:
            return "여유"
        if stock_quantity == 0:
            return "고갈"
        if stock_quantity < pending_qty:
            return "부족"
        return "여유"
