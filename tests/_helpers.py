from sample_order_system.controller.main_controller import MainController
from sample_order_system.model.clock import FakeClock
from sample_order_system.model.order_repository import OrderRepository
from sample_order_system.model.production_state_repository import ProductionStateRepository
from sample_order_system.model.sample_repository import SampleRepository


def make_controller(tmp_path, clock=None) -> MainController:
    return MainController(
        sample_repository=SampleRepository(tmp_path / "samples.json"),
        order_repository=OrderRepository(tmp_path / "orders.json"),
        production_state_repository=ProductionStateRepository(tmp_path / "production_state.json"),
        clock=clock or FakeClock(),
    )


def register_sample(controller: MainController, stock: int = 0, avg_production_time: float = 2.0, yield_rate: float = 0.9):
    sample = controller.sample_controller.register_sample("웨이퍼", avg_production_time, yield_rate)
    if stock:
        sample.stock_quantity = stock
        controller.sample_repository.save(sample)
    return sample
