from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

from sample_order_system.model.order import Order, OrderStatus
from sample_order_system.model.order_repository import OrderRepository
from sample_order_system.model.production_state_repository import ProductionStateRepository
from sample_order_system.model.sample import Sample
from sample_order_system.model.sample_repository import SampleRepository

DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

SAMPLE_NAME_POOL = [
    "실리콘웨이퍼", "게르마늄기판", "질화갈륨소자", "실리콘카바이드칩", "사파이어기판",
    "갈륨비소소자", "인듐인기판", "폴리실리콘시료", "산화막웨이퍼", "탄화규소소자",
]
CUSTOMER_NAME_POOL = [
    "서울반도체연구소", "한빛팹리스", "대한대학교 소재공학과", "케이테크연구원", "미래팹리스",
    "국립전자연구소", "신성반도체", "청록소재연구소", "한국나노기술원", "그린실리콘",
]

# PRODUCING은 production_state.json의 큐/활성 항목과 짝을 이뤄야 하므로 더미 데이터 상태 풀에서 제외한다.
DUMMY_ORDER_STATUSES = [
    OrderStatus.RESERVED,
    OrderStatus.REJECTED,
    OrderStatus.CONFIRMED,
    OrderStatus.RELEASE,
]


def generate_samples(repository: SampleRepository, count: int) -> list[Sample]:
    created = []
    for _ in range(count):
        sample = Sample(
            sample_id=repository.next_id(),
            name=random.choice(SAMPLE_NAME_POOL),
            avg_production_time=round(random.uniform(1.0, 10.0), 1),
            yield_rate=round(random.uniform(0.5, 1.0), 2),
            stock_quantity=random.randint(0, 100),
        )
        created.append(repository.create(sample))
    return created


def generate_orders(repository: OrderRepository, samples: list[Sample], count: int) -> list[Order]:
    if not samples:
        return []
    created = []
    for _ in range(count):
        sample = random.choice(samples)
        order = Order(
            order_id=repository.next_id(),
            sample_id=sample.sample_id,
            customer_name=random.choice(CUSTOMER_NAME_POOL),
            quantity=random.randint(1, 50),
            status=random.choice(DUMMY_ORDER_STATUSES),
        )
        created.append(repository.create(order))
    return created


def reset_data(data_dir: Path) -> None:
    for filename in ("samples.json", "orders.json", "production_state.json"):
        path = data_dir / filename
        if path.exists():
            path.unlink()


def run(samples_count: int, orders_count: int, reset: bool, data_dir: Path = DEFAULT_DATA_DIR) -> None:
    if samples_count < 0 or orders_count < 0:
        raise ValueError(f"--samples/--orders는 0 이상이어야 합니다 (samples={samples_count}, orders={orders_count}).")

    if reset:
        reset_data(data_dir)

    sample_repository = SampleRepository(data_dir / "samples.json")
    order_repository = OrderRepository(data_dir / "orders.json")
    ProductionStateRepository(data_dir / "production_state.json")  # 파일 존재만 보장, 내용은 건드리지 않음

    new_samples = generate_samples(sample_repository, samples_count)
    all_samples = sample_repository.list_all()
    new_orders = generate_orders(order_repository, all_samples, orders_count)

    print(f"시료 {len(new_samples)}건, 주문 {len(new_orders)}건 생성 완료 (데이터 경로: {data_dir})")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Dummy 데이터 생성 Tool (시료/주문)")
    parser.add_argument("--samples", type=int, default=10, help="생성할 시료 개수 (기본 10)")
    parser.add_argument("--orders", type=int, default=20, help="생성할 주문 개수 (기본 20)")
    parser.add_argument("--reset", action="store_true", help="기존 JSON 데이터를 초기화 후 생성")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR, help="데이터 디렉터리 경로")
    args = parser.parse_args()

    try:
        run(args.samples, args.orders, args.reset, args.data_dir)
    except ValueError as e:
        print(f"오류: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
