from __future__ import annotations

from sample_order_system.controller.monitoring_controller import MonitoringController
from sample_order_system.controller.order_controller import OrderController
from sample_order_system.controller.production_controller import ProductionController
from sample_order_system.controller.sample_controller import SampleController
from sample_order_system.controller.shipping_controller import ShippingController
from sample_order_system.model.clock import Clock, SystemClock
from sample_order_system.model.order_repository import OrderRepository
from sample_order_system.model.production_state_repository import ProductionStateRepository
from sample_order_system.model.sample_repository import SampleRepository


class MainController:
    def __init__(
        self,
        sample_repository: SampleRepository | None = None,
        order_repository: OrderRepository | None = None,
        production_state_repository: ProductionStateRepository | None = None,
        clock: Clock | None = None,
    ) -> None:
        self.sample_repository = sample_repository or SampleRepository()
        self.order_repository = order_repository or OrderRepository()
        self.production_state_repository = production_state_repository or ProductionStateRepository()
        self.clock = clock or SystemClock()

        self.sample_controller = SampleController(self.sample_repository)
        self.production_controller = ProductionController(
            self.sample_repository,
            self.order_repository,
            self.production_state_repository,
            clock=self.clock,
        )
        self.order_controller = OrderController(
            self.sample_repository,
            self.order_repository,
            self.production_controller,
        )
        self.shipping_controller = ShippingController(self.order_repository)
        self.monitoring_controller = MonitoringController(self.sample_repository, self.order_repository)

    def get_summary(self) -> dict:
        samples = self.sample_repository.list_all()
        orders = self.order_repository.list_all()
        return {
            "sample_count": len(samples),
            "total_stock": sum(s.stock_quantity for s in samples),
            "order_count": len(orders),
            "production_queue_count": len(self.production_controller.get_waiting_queue())
            + (1 if self.production_controller.get_active_status() else 0),
        }
