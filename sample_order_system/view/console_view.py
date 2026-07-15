from __future__ import annotations

from sample_order_system.controller.main_controller import MainController
from sample_order_system.model.order import Order, OrderStatus
from sample_order_system.view.colors import (
    CYAN,
    YELLOW,
    colorize,
    failure,
    muted,
    status_text,
    success,
    tier_text,
)
from sample_order_system.view.table import pad, render_bar, render_table

BANNER = r"""
      ___________________
     |  _______________  |
     | |###############| |
     | |###  S-Semi  ###| |
     | |###############| |
     |___________________|
        |  |  |  |  |  |
"""


class ConsoleView:
    def __init__(self) -> None:
        self.controller = MainController()

    def run(self) -> None:
        self._print_banner()
        while True:
            self._report_completions(self.controller.production_controller.tick())
            self._print_summary()
            self._print_main_menu()
            choice = input("메뉴 선택> ").strip()
            print()

            if choice == "0":
                break
            elif choice == "1":
                self._sample_menu()
            elif choice == "2":
                self._order_menu()
            elif choice == "3":
                self._monitoring_menu()
            elif choice == "4":
                self._shipping_menu()
            elif choice == "5":
                self._production_menu()
            else:
                print(failure("올바르지 않은 메뉴입니다."))
                print()

    # -- 출력 헬퍼 --------------------------------------------------------

    def _print_table(self, headers: list[str], rows: list[list[str]], aligns: list[str] | None = None) -> None:
        for line in render_table(headers, rows, aligns):
            print(line)
        print()

    def _print_banner(self) -> None:
        print(colorize(BANNER, CYAN))
        print(colorize("  반도체 시료 생산주문관리 시스템".center(40), CYAN))
        print()

    def _print_summary(self) -> None:
        summary = self.controller.get_summary()
        print("=" * 40)
        print(f"시료      : {summary['sample_count']}종")
        print(f"총 재고   : {summary['total_stock']}")
        print(f"전체 주문 : {summary['order_count']}건")
        print(f"생산 큐   : {summary['production_queue_count']}건")
        print("=" * 40)

        counts = self.controller.monitoring_controller.count_by_status()
        reserved_count = counts[OrderStatus.RESERVED.value]["count"]
        confirmed_count = counts[OrderStatus.CONFIRMED.value]["count"]
        if reserved_count > 0:
            print(colorize(f"🔔 승인/거절 대기 중인 주문이 {reserved_count}건 있습니다 (메뉴 2)", YELLOW))
        if confirmed_count > 0:
            print(colorize(f"📦 출고 대기 중인 주문이 {confirmed_count}건 있습니다 (메뉴 4)", CYAN))
        if reserved_count or confirmed_count:
            print()

    def _print_main_menu(self) -> None:
        items = [
            "1. 시료 관리",
            "2. 주문 (접수/승인/거절)",
            "3. 모니터링",
            "4. 출고 처리",
            "5. 생산 라인",
            "0. 종료",
        ]
        width = 36
        print("┌" + "─" * (width + 2) + "┐")
        for item in items:
            print("│ " + pad(item, width) + " │")
        print("└" + "─" * (width + 2) + "┘")

    def _report_completions(self, completed_orders: list[Order]) -> None:
        for order in completed_orders:
            print(success(f"[생산 완료] {order.order_id} → CONFIRMED"))

    # -- 입력 헬퍼 (빈 입력으로 취소, 잘못된 값은 같은 항목만 재입력) --------

    def _read_required(self, prompt: str) -> str | None:
        value = input(f"{prompt} (취소: Enter)> ").strip()
        return value or None

    def _read_int(self, prompt: str) -> int | None:
        while True:
            raw = input(f"{prompt} (취소: Enter)> ").strip()
            if not raw:
                return None
            try:
                return int(raw)
            except ValueError:
                print("숫자를 입력하세요.")

    def _read_float(self, prompt: str) -> float | None:
        while True:
            raw = input(f"{prompt} (취소: Enter)> ").strip()
            if not raw:
                return None
            try:
                return float(raw)
            except ValueError:
                print("숫자를 입력하세요.")

    # -- 시료 관리 -------------------------------------------------------

    def _sample_menu(self) -> None:
        while True:
            print("-- 시료 관리 --")
            print("1. 시료 등록")
            print("2. 시료 목록 조회")
            print("3. 시료 검색")
            print("0. 이전 메뉴")
            choice = input("선택> ").strip()
            print()

            if choice == "0":
                return
            elif choice == "1":
                self._register_sample()
            elif choice == "2":
                self._print_samples(self.controller.sample_controller.list_samples())
            elif choice == "3":
                keyword = self._read_required("검색어") or ""
                self._print_samples(self.controller.sample_controller.search_by_name(keyword))
            else:
                print(failure("올바르지 않은 메뉴입니다."))
                print()

    def _register_sample(self) -> None:
        name = self._read_required("시료 이름")
        if name is None:
            print(muted("취소되었습니다."))
            print()
            return
        avg_production_time = self._read_float("평균 생산시간(분)")
        if avg_production_time is None:
            print(muted("취소되었습니다."))
            print()
            return
        yield_rate = self._read_float("수율(0~1)")
        if yield_rate is None:
            print(muted("취소되었습니다."))
            print()
            return

        try:
            sample = self.controller.sample_controller.register_sample(name, avg_production_time, yield_rate)
            print(success(f"등록 완료: {sample.sample_id} ({sample.name})"))
        except ValueError as e:
            print(failure(f"등록 실패: {e}"))
        print()

    def _print_samples(self, samples) -> None:
        if not samples:
            print("등록된 시료가 없습니다.")
            print()
            return
        rows = [
            [s.sample_id, s.name, f"{s.avg_production_time:.1f}", f"{s.yield_rate:.2f}", str(s.stock_quantity)]
            for s in samples
        ]
        self._print_table(
            ["ID", "이름", "생산시간(분)", "수율", "재고"],
            rows,
            aligns=["left", "left", "right", "right", "right"],
        )

    # -- 주문 -------------------------------------------------------------

    def _order_menu(self) -> None:
        while True:
            print("-- 주문 (접수/승인/거절) --")
            print("1. 주문 접수")
            print("2. 접수된 주문 승인/거절")
            print("0. 이전 메뉴")
            choice = input("선택> ").strip()
            print()

            if choice == "0":
                return
            elif choice == "1":
                self._create_order()
            elif choice == "2":
                self._approve_or_reject_order()
            else:
                print(failure("올바르지 않은 메뉴입니다."))
                print()

    def _print_orders(self, orders: list[Order]) -> None:
        rows = [[o.order_id, o.sample_id, o.customer_name, str(o.quantity)] for o in orders]
        self._print_table(
            ["ID", "시료", "고객", "수량"],
            rows,
            aligns=["left", "left", "left", "right"],
        )

    def _create_order(self) -> None:
        sample_id = self._read_required("시료 ID")
        if sample_id is None:
            print(muted("취소되었습니다."))
            print()
            return
        customer_name = self._read_required("고객명")
        if customer_name is None:
            print(muted("취소되었습니다."))
            print()
            return
        quantity = self._read_int("주문 수량")
        if quantity is None:
            print(muted("취소되었습니다."))
            print()
            return

        try:
            order = self.controller.order_controller.create_order(sample_id, customer_name, quantity)
            print(success(f"접수 완료: {order.order_id} ({order.status.value})"))
        except ValueError as e:
            print(failure(f"접수 실패: {e}"))
        print()

    def _approve_or_reject_order(self) -> None:
        reserved = self.controller.order_controller.list_reserved_orders()
        if not reserved:
            print("RESERVED 상태의 주문이 없습니다.")
            print()
            return
        self._print_orders(reserved)

        order_id = self._read_required("대상 주문 ID")
        if order_id is None:
            print(muted("취소되었습니다."))
            print()
            return
        action = self._read_required("승인(a) / 거절(r)")
        if action is None:
            print(muted("취소되었습니다."))
            print()
            return
        action = action.lower()
        try:
            if action == "a":
                order = self.controller.order_controller.approve_order(order_id)
                print(success(f"승인 완료: {order.order_id} → ") + status_text(order.status.value))
            elif action == "r":
                order = self.controller.order_controller.reject_order(order_id)
                print(success(f"거절 완료: {order.order_id} → ") + status_text(order.status.value))
            else:
                print(failure("올바르지 않은 선택입니다."))
        except ValueError as e:
            print(failure(f"처리 실패: {e}"))
        print()

    # -- 모니터링 -----------------------------------------------------------

    def _monitoring_menu(self) -> None:
        print("-- 주문량 확인 --")
        counts = self.controller.monitoring_controller.count_by_status()
        max_quantity = max((stats["quantity"] for stats in counts.values()), default=0) or 1
        rows = [
            [
                status_text(status),
                str(stats["count"]),
                str(stats["quantity"]),
                render_bar(stats["quantity"] / max_quantity * 100, width=15),
            ]
            for status, stats in counts.items()
        ]
        self._print_table(
            ["상태", "건수", "수량", "비중(수량 기준)"],
            rows,
            aligns=["left", "right", "right", "left"],
        )

        print("-- 재고량 확인 --")
        inventory = self.controller.monitoring_controller.inventory_status()
        if not inventory:
            print("등록된 시료가 없습니다.")
            print()
            return
        rows = []
        for row in inventory:
            coverage = 100.0 if row["pending_qty"] == 0 else min(100.0, row["stock_quantity"] / row["pending_qty"] * 100)
            rows.append(
                [
                    row["sample_id"],
                    row["name"],
                    str(row["stock_quantity"]),
                    str(row["pending_qty"]),
                    render_bar(coverage, width=15),
                    tier_text(row["tier"]),
                ]
            )
        self._print_table(
            ["ID", "이름", "재고", "대기수량", "충족률", "상태"],
            rows,
            aligns=["left", "left", "right", "right", "left", "left"],
        )

    # -- 출고 처리 ---------------------------------------------------------

    def _shipping_menu(self) -> None:
        confirmed = self.controller.shipping_controller.list_confirmed_orders()
        if not confirmed:
            print("출고 대기 중인(CONFIRMED) 주문이 없습니다.")
            print()
            return
        self._print_orders(confirmed)

        order_id = self._read_required("출고할 주문 ID")
        if order_id is None:
            print(muted("취소되었습니다."))
            print()
            return
        try:
            order = self.controller.shipping_controller.ship_order(order_id)
            print(success(f"출고 완료: {order.order_id} → ") + status_text(order.status.value))
        except ValueError as e:
            print(failure(f"출고 실패: {e}"))
        print()

    # -- 생산 라인 ---------------------------------------------------------

    def _production_menu(self) -> None:
        self._report_completions(self.controller.production_controller.tick())

        print("-- 현재 생산 중 --")
        active = self.controller.production_controller.get_active_status()
        if active:
            self._print_table(
                ["주문", "시료", "고객", "주문수량", "부족분", "실생산량", "경과(분)", "총(분)", "남은(분)"],
                [[
                    active["order_id"],
                    f"{active['sample_name']}({active['sample_id']})",
                    active["customer_name"],
                    str(active["order_quantity"]),
                    str(active["shortage_qty"]),
                    str(active["target_qty"]),
                    f"{active['elapsed_minutes']:.2f}",
                    f"{active['total_minutes']:.2f}",
                    f"{active['remaining_minutes']:.2f}",
                ]],
                aligns=["left", "left", "left", "right", "right", "right", "right", "right", "right"],
            )
            print(colorize(render_bar(active["percent"]), CYAN))
            print()
        else:
            print("현재 생산 중인 항목이 없습니다.")
            print()

        print("-- 대기 큐 (FIFO) --")
        waiting = self.controller.production_controller.get_waiting_queue_status()
        if not waiting:
            print("대기 중인 항목이 없습니다.")
            print()
            return
        rows = [
            [
                str(row["position"]),
                row["order_id"],
                f"{row['sample_name']}({row['sample_id']})",
                row["customer_name"],
                str(row["order_quantity"]),
                str(row["shortage_qty"]),
                str(row["actual_production_qty"]),
                f"{row['total_minutes']:.2f}",
                f"{row['expected_wait_minutes']:.2f}",
            ]
            for row in waiting
        ]
        self._print_table(
            ["#", "주문", "시료", "고객", "주문수량", "부족분", "실생산량", "소요(분)", "대기(분)"],
            rows,
            aligns=["right", "left", "left", "left", "right", "right", "right", "right", "right"],
        )
