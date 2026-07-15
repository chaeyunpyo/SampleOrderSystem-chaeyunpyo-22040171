# 0012 — 생산 현황 표기 정보량 확대

**날짜**: 2026-07-15

**대상 작업**: 생산 라인 메뉴("현재 생산 중"/"대기 큐")에 표시되는 정보를 더 자세하게 확장. 사용자가 직접 `python main.py`로 생산 라인을 확인해보니 현재 표기(주문ID/시료명/목표수량/경과·총 시간/퍼센트)만으로는 정보가 부족하다고 판단.

**EXPLORE에서 확인한 사실/제약**:
- 현재 `ProductionController.get_active_status()`는 `order_id/sample_id/sample_name/target_qty/elapsed_minutes/total_minutes/percent`만 반환.
- `get_waiting_queue()`는 `ProductionQueueItem` 객체 리스트를 그대로 반환하고, View가 `order_id/sample_id/shortage_qty/actual_production_qty`만 출력.
- 고객명, 주문 수량(부족분과 별개인 원 주문량), 남은 시간, 대기 큐의 각 항목이 실제로 시작되기까지 예상 대기 시간이 전혀 표시되지 않음.
- PRD.md 4.5/8.1 "생산 현황 표기 수준"은 "구현 시 결정"으로 위임되어 있어 이번 확장은 스펙 위반이 아니라 그 위임 범위 내에서 표기 수준을 높이는 것.

**설계**:
- `get_active_status()`에 필드 추가: `customer_name`, `order_quantity`(원 주문 수량), `shortage_qty`(부족분), `remaining_minutes`(= total - elapsed, 0 미만 방지).
- 신규 `get_waiting_queue_status() -> list[dict]` 추가: 대기 큐 각 항목에 대해 `position`(1부터), `order_id`, `sample_id`, `customer_name`, `order_quantity`, `shortage_qty`, `actual_production_qty`, `total_minutes`, `expected_wait_minutes`(현재 활성 항목의 `remaining_minutes` + 자신보다 앞에 있는 대기 항목들의 `total_minutes` 합)를 담아 반환. 기존 `get_waiting_queue()`(원시 `ProductionQueueItem` 리스트)는 테스트 호환을 위해 그대로 둔다.
- `console_view._production_menu`를 위 필드들을 모두 표시하도록 갱신.

**실행 계획**:
1. `production_controller.py`에 `_order_and_sample(item)` 헬퍼 추가, `get_active_status()` 필드 확장, `get_waiting_queue_status()` 신규 추가.
2. `console_view.py`의 `_production_menu` 출력 갱신.
3. `tests/test_production_fifo_and_single_line.py`에 새 필드/신규 메서드에 대한 검증 추가 (혹은 신규 테스트 파일).
4. domain-reviewer 관점 리뷰, spec-guardian 관점 PRD.md 대조(표기 수준 확장이 4.5/8.1 위임 범위 내인지).
5. `pytest` 전체 통과 확인, `python main.py`로 수동 확인 후 커밋.

**상태**: ACTION 완료 (`get_active_status`/`get_waiting_queue_status` 필드 확장, `console_view._production_menu` 출력 갱신, 테스트 4개 추가, 전체 53개 테스트 통과, `python -c` 드라이버로 실제 출력 형태 수동 확인, PRD.md 4.5/8.1 갱신). COMMIT 완료 — `258c5da`(controller/view), `2eeffa6`(테스트).
