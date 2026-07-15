# 0008 — MVC 골격 구현 (Model/Controller/View + JSON 영속성 + 테스트)

**날짜**: 2026-07-15

**대상 작업**: `sample_order_system/{model,controller,view}` + `main.py` + `tests/` + `data/` 구현. `tools/`(더미데이터 생성기, 모니터 스크립트)는 이번 범위에서 제외하고 다음 항목(0009)으로 분리.

**EXPLORE에서 확인한 사실/제약**:
- ConsoleMVC PoC(참조 전용, `C:\reviewer\mission\ConsoleMVC-chaeyunpyo-22040171`)의 model/controller/view 구조와 상태 전이 로직(`OrderStatus` enum, `approve_order`의 재고 분기)을 MVC/상태기계 템플릿으로 참고.
- DataPersistence PoC(참조 전용, `C:\reviewer\mission\DataPersistence-chaeyunpyo-22040171`)의 JSON 리포지토리 CRUD/직렬화 패턴을 영속성 템플릿으로 참고하되, non-atomic 저장은 개선(임시파일+`os.replace`).
- 두 PoC 간 필드명 불일치(`stock` vs `stock_quantity`) 발견 — 이 프로젝트는 PRD/DataPersistence를 따라 `stock_quantity`로 통일.
- ConsoleMVC의 재고 부족 승인 시 "재고를 0으로 초기화"하는 라인은 PRD의 차감 시점 규칙과 맞지 않아 이식하지 않기로 함.

**확정된 결정** (이번 대화에서 사용자 확정):
- ID 형식: `sample_id`는 `S0001`, `S0002`...; `order_id`는 `O0001`, `O0002`... (각 리포지토리가 로드된 키의 숫자 접미사 최댓값+1로 계산, 별도 카운터 파일 불필요).
- 생산 완료 처리: 수동 트리거가 아니라 Mock Clock 시스템 (`Clock` 프로토콜 + `SystemClock`/`FakeClock`). 실제 sleep 없이 메뉴 렌더링 시마다 `ProductionController.tick()`으로 경과시간 체크 후 자동 완료.
- 생산시간 단위: 분(minute).
- 이번 사이클 범위: `tools/` 제외.
- 재고 티어 경계 규칙 추가: `pending_qty == 0`이면 재고가 0이어도 "여유"로 처리 (대기 물량이 없으므로).
- 모니터링 `count_by_status`는 건수와 수량 합계 모두 반환 (PRD "건수(및 수량)" 반영).

**실행 계획**:
1. Model: `order.py`(OrderStatus, Order), `sample.py`(Sample dataclass, stock_quantity), `production_queue.py`(ProductionQueueItem, ceil/총생산시간), `clock.py`(Clock/SystemClock/FakeClock), `sample_repository.py`/`order_repository.py`/`production_state_repository.py` (JSON 원자적 쓰기, `next_id()`).
2. Controller: `sample_controller.py`, `order_controller.py`(approve_order 재고 분기, `_get_order_in_status` 가드), `production_controller.py`(enqueue/tick/get_active_status/get_waiting_queue), `shipping_controller.py`, `monitoring_controller.py`(count_by_status, inventory_status), `main_controller.py`(get_summary, wiring).
3. View: `console_view.py` 5개 메뉴(시료관리/주문/모니터링/출고/생산라인) + `main.py`.
4. `tests/`: test_order_state_transitions.py, test_stock_deduction_timing.py, test_production_queue_calculations.py, test_production_fifo_and_single_line.py(FakeClock), test_inventory_status_tiers.py, test_monitoring_excludes_rejected.py, test_json_persistence.py(tmp_path), test_id_generation.py.
5. domain-reviewer 관점으로 구현 리뷰, spec-guardian 관점으로 PRD.md 대조 검증(1차: 착수 전 설계, 2차: 커밋 전 최종), test-writer 관점으로 테스트 작성/실행.
6. PRD.md 4.7절에 재고 티어 `pending_qty==0` 경계 규칙을 새 설계 결정으로 추가 기록.

**미해결 질문**: 없음 (이번 사이클 관련 설계 결정은 모두 확정됨).

**상태**: ACTION 완료 (Model/Controller/View/main.py/tests 34개 전부 통과, domain-reviewer 리뷰로 단일 생산 라인 관련 테스트 시나리오 1건 수정, spec-guardian 1·2차 검증 통과). COMMIT 완료 — `cc6d15a`(모델/리포지토리), `7d70060`(컨트롤러), `6125863`(뷰/main.py), `adca791`(테스트), `9b44691`(PRD/plans 문서 갱신).
