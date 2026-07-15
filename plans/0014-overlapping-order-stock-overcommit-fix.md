# 0014 — 겹치는 주문/생산 처리 시 재고 이중 소진(overcommit) 버그 수정

**날짜**: 2026-07-15

**대상 작업**: 같은 시료에 대해 재고 부족 상태의 주문이 여러 건 겹칠 때 재고가 음수로 떨어지는 정합성 버그 수정.

**EXPLORE에서 확인한 사실/제약 (직접 재현으로 확인)**:

시나리오 1 — 부족 주문 2건이 겹칠 때:
```
stock=2
OrderA(qty5) 승인 → 부족(2<5) → shortage=3, PRODUCING, 재고는 그대로 2
OrderB(qty3) 승인 → 같은 2를 기준으로 다시 부족 판정(2<3) → shortage=1, PRODUCING, 재고 여전히 2
A 완료: stock += actual_A(3, yield=1) - qty_A(5) = 2+3-5 = 0
B 완료: stock += actual_B(1, yield=1) - qty_B(3) = 0+1-3 = -2   ← 음수 재고
```

시나리오 2 — 부족 주문이 큐에 있는 동안 같은 시료의 다른 주문이 "충분"으로 즉시 승인되는 경우도 동일 근본 원인으로 음수 재고 발생 (직접 검증).

근본 원인: `approve_order`의 재고 부족 경로가 `shortage_qty`만 계산하고 `stock_quantity`를 그대로 두기 때문에, 뒤이은 주문들이 이미 "쓰일 예정인" 재고를 다시 사용 가능한 것으로 잘못 인식한다.

**수정 (수학적으로 검증)**:
- `approve_order` 부족 경로: 승인 시점에 남아있던 재고 전량을 즉시 이 주문에 귀속시켜 `stock_quantity = 0`으로 만든다.
- `_complete_active`: `stock += actual_production_qty; stock -= order.quantity` 대신 `stock += (actual_production_qty - shortage_qty)`로 변경 (수율 반올림 초과분만 재고로 환원, `shortage_qty`만큼은 이미 이 주문 몫).
- 단일/비중첩 케이스에서는 대수적으로 `0 + (actual-shortage) = old_stock + actual - quantity`와 동치 — 기존 테스트 결과 불변.
- 중첩 케이스에서는 재고가 정확히 맞아떨어짐 (재현 예시 재계산 시 양쪽 다 0, 음수 없음).

**PRD.md 영향**: 4.4/8.1의 "PRODUCING 전환 시 재고 차감 없음"을 "PRODUCING 전환 시 남은 재고 전량을 해당 주문에 선점(귀속)시켜 0으로 만듦(같은 시료의 다른 주문이 이중으로 사용하지 못하도록) — 이는 재고 확정 차감이 아니라 이중 사용 방지를 위한 선점이며, 실제 확정은 여전히 CONFIRMED 전환 시점 개념과 일치"로 갱신.

**실행 계획**:
1. `order_controller.py` approve_order 수정.
2. `production_controller.py` `_complete_active` 수정.
3. `tests/test_overlapping_orders_stock.py` 신규 — 두 시나리오 회귀 테스트.
4. 기존 테스트 전체 재실행, 회귀 없음 확인.
5. `PRD.md` 4.4/8.1 갱신.
6. domain-reviewer/spec-guardian 관점 재검토.
7. 의미 단위 커밋.

**상태**: ACTION 완료 (`order_controller.py`/`production_controller.py` 수정, 회귀 테스트 2건 추가, 기존 테스트 이름/기대값 갱신, 전체 61개 테스트 통과, 재현 스크립트로 최종 재고가 음수 아님을 직접 재확인, PRD.md 4.4/4.5/8.1 갱신). COMMIT 완료 — `9c3ad80`(컨트롤러 수정), `1dbdd3a`(테스트).
