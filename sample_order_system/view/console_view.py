from __future__ import annotations

from sample_order_system.controller.main_controller import MainController
from sample_order_system.model.order import Order


class ConsoleView:
    def __init__(self) -> None:
        self.controller = MainController()

    def run(self) -> None:
        while True:
            self._report_completions(self.controller.production_controller.tick())
            self._print_summary()
            self._print_main_menu()
            choice = input("메뉴 선택> ").strip()

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
                print("올바르지 않은 메뉴입니다.\n")

    # -- 요약/메인 메뉴 -------------------------------------------------

    def _print_summary(self) -> None:
        summary = self.controller.get_summary()
        print("=" * 40)
        print(
            f"시료 {summary['sample_count']}종 | 총 재고 {summary['total_stock']} | "
            f"전체 주문 {summary['order_count']}건 | 생산 큐 {summary['production_queue_count']}건"
        )
        print("=" * 40)

    def _print_main_menu(self) -> None:
        print("1. 시료 관리")
        print("2. 주문 (접수/승인/거절)")
        print("3. 모니터링")
        print("4. 출고 처리")
        print("5. 생산 라인")
        print("0. 종료")

    def _report_completions(self, completed_orders: list[Order]) -> None:
        for order in completed_orders:
            print(f"[생산 완료] {order.order_id} → CONFIRMED")

    # -- 시료 관리 -------------------------------------------------------

    def _sample_menu(self) -> None:
        while True:
            print("\n-- 시료 관리 --")
            print("1. 시료 등록")
            print("2. 시료 목록 조회")
            print("3. 시료 검색")
            print("0. 이전 메뉴")
            choice = input("선택> ").strip()

            if choice == "0":
                return
            elif choice == "1":
                self._register_sample()
            elif choice == "2":
                self._print_samples(self.controller.sample_controller.list_samples())
            elif choice == "3":
                keyword = input("검색어 입력> ").strip()
                self._print_samples(self.controller.sample_controller.search_by_name(keyword))
            else:
                print("올바르지 않은 메뉴입니다.")

    def _register_sample(self) -> None:
        try:
            name = input("시료 이름> ").strip()
            avg_production_time = float(input("평균 생산시간(분)> ").strip())
            yield_rate = float(input("수율(0~1)> ").strip())
            sample = self.controller.sample_controller.register_sample(name, avg_production_time, yield_rate)
            print(f"등록 완료: {sample.sample_id} ({sample.name})")
        except ValueError as e:
            print(f"등록 실패: {e}")

    def _print_samples(self, samples) -> None:
        if not samples:
            print("등록된 시료가 없습니다.")
            return
        for s in samples:
            print(
                f"{s.sample_id} | {s.name} | 평균생산시간 {s.avg_production_time}분 | "
                f"수율 {s.yield_rate} | 재고 {s.stock_quantity}"
            )

    # -- 주문 -------------------------------------------------------------

    def _order_menu(self) -> None:
        while True:
            print("\n-- 주문 (접수/승인/거절) --")
            print("1. 주문 접수")
            print("2. 접수된 주문 승인/거절")
            print("0. 이전 메뉴")
            choice = input("선택> ").strip()

            if choice == "0":
                return
            elif choice == "1":
                self._create_order()
            elif choice == "2":
                self._approve_or_reject_order()
            else:
                print("올바르지 않은 메뉴입니다.")

    def _create_order(self) -> None:
        try:
            sample_id = input("시료 ID> ").strip()
            customer_name = input("고객명> ").strip()
            quantity = int(input("주문 수량> ").strip())
            order = self.controller.order_controller.create_order(sample_id, customer_name, quantity)
            print(f"접수 완료: {order.order_id} (RESERVED)")
        except ValueError as e:
            print(f"접수 실패: {e}")

    def _approve_or_reject_order(self) -> None:
        reserved = self.controller.order_controller.list_reserved_orders()
        if not reserved:
            print("RESERVED 상태의 주문이 없습니다.")
            return
        for o in reserved:
            print(f"{o.order_id} | 시료 {o.sample_id} | 고객 {o.customer_name} | 수량 {o.quantity}")

        order_id = input("대상 주문 ID> ").strip()
        action = input("승인(a) / 거절(r)> ").strip().lower()
        try:
            if action == "a":
                order = self.controller.order_controller.approve_order(order_id)
                print(f"승인 완료: {order.order_id} → {order.status.value}")
            elif action == "r":
                order = self.controller.order_controller.reject_order(order_id)
                print(f"거절 완료: {order.order_id} → {order.status.value}")
            else:
                print("올바르지 않은 선택입니다.")
        except ValueError as e:
            print(f"처리 실패: {e}")

    # -- 모니터링 -----------------------------------------------------------

    def _monitoring_menu(self) -> None:
        counts = self.controller.monitoring_controller.count_by_status()
        print("\n-- 주문량 확인 --")
        for status, stats in counts.items():
            print(f"{status}: {stats['count']}건 / 수량 {stats['quantity']}")

        print("\n-- 재고량 확인 --")
        inventory = self.controller.monitoring_controller.inventory_status()
        if not inventory:
            print("등록된 시료가 없습니다.")
            return
        for row in inventory:
            print(
                f"{row['sample_id']} | {row['name']} | 재고 {row['stock_quantity']} | "
                f"대기수량 {row['pending_qty']} | 상태 {row['tier']}"
            )

    # -- 출고 처리 ---------------------------------------------------------

    def _shipping_menu(self) -> None:
        confirmed = self.controller.shipping_controller.list_confirmed_orders()
        if not confirmed:
            print("출고 대기 중인(CONFIRMED) 주문이 없습니다.")
            return
        for o in confirmed:
            print(f"{o.order_id} | 시료 {o.sample_id} | 고객 {o.customer_name} | 수량 {o.quantity}")

        order_id = input("출고할 주문 ID> ").strip()
        try:
            order = self.controller.shipping_controller.ship_order(order_id)
            print(f"출고 완료: {order.order_id} → {order.status.value}")
        except ValueError as e:
            print(f"출고 실패: {e}")

    # -- 생산 라인 ---------------------------------------------------------

    def _production_menu(self) -> None:
        self._report_completions(self.controller.production_controller.tick())

        active = self.controller.production_controller.get_active_status()
        print("\n-- 현재 생산 중 --")
        if active:
            print(
                f"{active['order_id']} | 시료 {active['sample_name']} | 목표수량 {active['target_qty']} | "
                f"경과 {active['elapsed_minutes']}/{active['total_minutes']}분 ({active['percent']}%)"
            )
        else:
            print("현재 생산 중인 항목이 없습니다.")

        waiting = self.controller.production_controller.get_waiting_queue()
        print("\n-- 대기 큐 (FIFO) --")
        if not waiting:
            print("대기 중인 항목이 없습니다.")
            return
        for i, item in enumerate(waiting, start=1):
            print(
                f"{i}. {item.order_id} | 시료 {item.sample_id} | 부족분 {item.shortage_qty} → "
                f"실생산량 {item.actual_production_qty}"
            )
