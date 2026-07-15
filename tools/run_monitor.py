from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from sample_order_system.controller.monitoring_controller import MonitoringController
from sample_order_system.model.order_repository import OrderRepository
from sample_order_system.model.sample_repository import SampleRepository

DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def render_once(data_dir: Path) -> str:
    sample_repository = SampleRepository(data_dir / "samples.json")
    order_repository = OrderRepository(data_dir / "orders.json")
    monitoring_controller = MonitoringController(sample_repository, order_repository)

    counts = monitoring_controller.count_by_status()
    inventory = monitoring_controller.inventory_status()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [f"[{now}] 데이터 모니터링 ({data_dir})", ""]
    lines.append("-- 주문량 확인 --")
    lines.append(f"{'상태':<12}{'건수':>8}{'수량':>10}")
    for status, stats in counts.items():
        lines.append(f"{status:<12}{stats['count']:>8}{stats['quantity']:>10}")

    lines.append("")
    lines.append("-- 재고량 확인 --")
    if not inventory:
        lines.append("등록된 시료가 없습니다.")
    else:
        lines.append(f"{'시료ID':<8}{'이름':<16}{'재고':>8}{'대기수량':>10}{'상태':>8}")
        for row in inventory:
            lines.append(
                f"{row['sample_id']:<8}{row['name']:<16}{row['stock_quantity']:>8}"
                f"{row['pending_qty']:>10}{row['tier']:>8}"
            )

    return "\n".join(lines)


def _clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def run(data_dir: Path, interval: float, once: bool) -> None:
    if not once and interval <= 0:
        raise ValueError(f"--interval은 0보다 커야 합니다 (입력값: {interval}).")

    if once:
        print(render_once(data_dir))
        return

    try:
        while True:
            _clear_screen()
            print(render_once(data_dir))
            print(f"\n(Ctrl+C로 종료, {interval}초마다 갱신)")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n모니터링 종료")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="데이터 모니터링 Tool")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR, help="데이터 디렉터리 경로")
    parser.add_argument("--interval", type=float, default=2.0, help="갱신 주기(초, 기본 2.0)")
    parser.add_argument("--once", action="store_true", help="한 번만 조회하고 종료")
    args = parser.parse_args()

    try:
        run(args.data_dir, args.interval, args.once)
    except ValueError as e:
        print(f"오류: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
