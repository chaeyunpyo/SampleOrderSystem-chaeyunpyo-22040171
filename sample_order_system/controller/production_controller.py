from __future__ import annotations

from sample_order_system.model.clock import Clock, SystemClock
from sample_order_system.model.order import Order, OrderStatus
from sample_order_system.model.order_repository import OrderRepository
from sample_order_system.model.production_queue import ProductionQueueItem
from sample_order_system.model.production_state_repository import ProductionStateRepository
from sample_order_system.model.sample import Sample
from sample_order_system.model.sample_repository import SampleRepository


class ProductionController:
    def __init__(
        self,
        sample_repository: SampleRepository,
        order_repository: OrderRepository,
        production_state_repository: ProductionStateRepository,
        clock: Clock | None = None,
    ) -> None:
        self.sample_repository = sample_repository
        self.order_repository = order_repository
        self.production_state_repository = production_state_repository
        self.clock = clock or SystemClock()
        self._queue, self._active = self.production_state_repository.load()

    def enqueue(self, order: Order, sample: Sample, shortage_qty: int) -> ProductionQueueItem:
        item = ProductionQueueItem(
            order_id=order.order_id,
            sample_id=sample.sample_id,
            shortage_qty=shortage_qty,
            avg_production_time=sample.avg_production_time,
            yield_rate=sample.yield_rate,
            enqueued_at=self.clock.now(),
        )
        self._queue.append(item)
        self._persist_state()
        return item

    def tick(self) -> list[Order]:
        completed: list[Order] = []
        while True:
            if self._active is None:
                if not self._queue:
                    break
                self._active = self._queue.pop(0)
                self._active.started_at = self.clock.now()
                self._persist_state()

            elapsed_minutes = (self.clock.now() - self._active.started_at).total_seconds() / 60
            if elapsed_minutes < self._active.total_production_time:
                break

            completed.append(self._complete_active())

        return completed

    def _complete_active(self) -> Order:
        item = self._active
        order, sample = self._order_and_sample(item)

        sample.stock_quantity += item.actual_production_qty
        sample.stock_quantity -= order.quantity
        self.sample_repository.save(sample)

        order.status = OrderStatus.CONFIRMED
        self.order_repository.save(order)

        self._active = None
        self._persist_state()
        return order

    def get_active_status(self) -> dict | None:
        if self._active is None:
            return None
        item = self._active
        order, sample = self._order_and_sample(item)
        elapsed_minutes = (self.clock.now() - item.started_at).total_seconds() / 60
        elapsed_minutes = min(elapsed_minutes, item.total_production_time)
        remaining_minutes = max(item.total_production_time - elapsed_minutes, 0.0)
        percent = (
            100.0
            if item.total_production_time == 0
            else round(elapsed_minutes / item.total_production_time * 100, 1)
        )
        return {
            "order_id": item.order_id,
            "sample_id": item.sample_id,
            "sample_name": sample.name,
            "customer_name": order.customer_name,
            "order_quantity": order.quantity,
            "shortage_qty": item.shortage_qty,
            "target_qty": item.actual_production_qty,
            "elapsed_minutes": round(elapsed_minutes, 2),
            "remaining_minutes": round(remaining_minutes, 2),
            "total_minutes": item.total_production_time,
            "percent": percent,
        }

    def get_waiting_queue(self) -> list[ProductionQueueItem]:
        return list(self._queue)

    def get_waiting_queue_status(self) -> list[dict]:
        active_status = self.get_active_status()
        expected_wait = active_status["remaining_minutes"] if active_status else 0.0

        result = []
        for position, item in enumerate(self._queue, start=1):
            order, sample = self._order_and_sample(item)
            result.append(
                {
                    "position": position,
                    "order_id": item.order_id,
                    "sample_id": item.sample_id,
                    "sample_name": sample.name,
                    "customer_name": order.customer_name,
                    "order_quantity": order.quantity,
                    "shortage_qty": item.shortage_qty,
                    "actual_production_qty": item.actual_production_qty,
                    "total_minutes": item.total_production_time,
                    "expected_wait_minutes": round(expected_wait, 2),
                }
            )
            expected_wait += item.total_production_time

        return result

    def _order_and_sample(self, item: ProductionQueueItem) -> tuple[Order, Sample]:
        order = self.order_repository.get(item.order_id)
        sample = self.sample_repository.get(item.sample_id)
        return order, sample

    def _persist_state(self) -> None:
        self.production_state_repository.save(self._queue, self._active)
