from __future__ import annotations

from sample_order_system.controller.production_controller import ProductionController
from sample_order_system.model.order import Order, OrderStatus
from sample_order_system.model.order_repository import OrderNotFoundError, OrderRepository
from sample_order_system.model.sample_repository import SampleNotFoundError, SampleRepository


class OrderController:
    def __init__(
        self,
        sample_repository: SampleRepository,
        order_repository: OrderRepository,
        production_controller: ProductionController,
    ) -> None:
        self.sample_repository = sample_repository
        self.order_repository = order_repository
        self.production_controller = production_controller

    def create_order(self, sample_id: str, customer_name: str, quantity: int) -> Order:
        try:
            self.sample_repository.get(sample_id)
        except SampleNotFoundError:
            raise ValueError(f"존재하지 않는 시료입니다: {sample_id}") from None
        if quantity <= 0:
            raise ValueError("주문 수량은 0보다 커야 합니다.")

        order_id = self.order_repository.next_id()
        order = Order(order_id=order_id, sample_id=sample_id, customer_name=customer_name, quantity=quantity)
        return self.order_repository.create(order)

    def list_reserved_orders(self) -> list[Order]:
        return [o for o in self.order_repository.list_all() if o.status == OrderStatus.RESERVED]

    def reject_order(self, order_id: str) -> Order:
        order = self._get_order_in_status(order_id, OrderStatus.RESERVED)
        order.status = OrderStatus.REJECTED
        return self.order_repository.save(order)

    def approve_order(self, order_id: str) -> Order:
        order = self._get_order_in_status(order_id, OrderStatus.RESERVED)
        sample = self.sample_repository.get(order.sample_id)

        if sample.stock_quantity >= order.quantity:
            sample.stock_quantity -= order.quantity
            self.sample_repository.save(sample)
            order.status = OrderStatus.CONFIRMED
        else:
            shortage_qty = order.quantity - sample.stock_quantity
            self.production_controller.enqueue(order, sample, shortage_qty)
            order.status = OrderStatus.PRODUCING

        return self.order_repository.save(order)

    def _get_order_in_status(self, order_id: str, expected_status: OrderStatus) -> Order:
        try:
            order = self.order_repository.get(order_id)
        except OrderNotFoundError:
            raise ValueError(f"존재하지 않는 주문입니다: {order_id}") from None
        if order.status != expected_status:
            raise ValueError(f"{order_id} 주문은 {expected_status.value} 상태가 아닙니다 (현재: {order.status.value}).")
        return order
