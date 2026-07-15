from __future__ import annotations

from sample_order_system.model.order import Order, OrderStatus
from sample_order_system.model.order_repository import OrderNotFoundError, OrderRepository


class ShippingController:
    def __init__(self, order_repository: OrderRepository) -> None:
        self.order_repository = order_repository

    def list_confirmed_orders(self) -> list[Order]:
        return [o for o in self.order_repository.list_all() if o.status == OrderStatus.CONFIRMED]

    def ship_order(self, order_id: str) -> Order:
        try:
            order = self.order_repository.get(order_id)
        except OrderNotFoundError:
            raise ValueError(f"존재하지 않는 주문입니다: {order_id}") from None
        if order.status != OrderStatus.CONFIRMED:
            raise ValueError(f"{order_id} 주문은 CONFIRMED 상태가 아닙니다 (현재: {order.status.value}).")

        order.status = OrderStatus.RELEASE
        return self.order_repository.save(order)
