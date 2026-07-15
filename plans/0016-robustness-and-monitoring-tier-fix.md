# 0016 — 견고성 수정 (크래시 방지) + 모니터링 재고 티어 로직 보정

**날짜**: 2026-07-15

**대상 작업**: 전체 프로세스 조사(3개 병렬 조사: Model/영속성, Controller, View/CLI/tools)에서 발견한 예외 케이스 중 실사용에 영향을 주는 항목들을 심각도 순으로 수정. 사소하거나 실제 도달 경로가 없는 항목(ID 채번 대소문자, FakeClock 음수 시간, 동시 다중 프로세스 충돌, 파일 권한/디스크풀 등)은 손대지 않는다.

**EXPLORE — 조사에서 확인한 사실(3개 fork 종합)**:
- 손상된 JSON/필드 누락/파싱 실패(json.JSONDecodeError, KeyError, ValueError from datetime/enum)가 앱 시작 시 그대로 크래시.
- `_read_required`/`_read_int`/`_read_float`가 EOFError를 안 잡고, 메인 루프도 KeyboardInterrupt를 안 잡아 Ctrl+C/stdin 종료 시 트레이스백 노출.
- 생산 큐가 참조하는 주문/시료가 사라지면(수동 파일 편집 등) `tick()`/`get_active_status()`/`get_waiting_queue_status()`가 크래시 — 매 메뉴 렌더링마다 호출되므로 앱이 아예 안 켜짐.
- (신규, 0014 이후 발생) `MonitoringController._inventory_tier`가 CONFIRMED 주문 수량(이미 0014에서 재고에서 선점·차감된 확정분)을 다시 "미확보 수요"인 것처럼 재고와 비교해 "부족/고갈"로 오판.
- `tools/run_monitor.py --interval`에 음수를 주면 `time.sleep()`이 ValueError로 크래시.
- `table.py`의 `render_table`이 헤더/행/aligns 길이가 어긋나면 IndexError (현재 호출부는 다 맞춰서 넘기지만 방어 코드 없음).
- `tools/dummy_data_generator.py --samples/--orders`에 음수를 줘도 조용히 무시(경고 없음).

**수정 방향**:
1. `sample_order_system/model/errors.py` 신규: `DataIntegrityError`. 3개 리포지토리의 로드 경로가 json/구조/파싱 오류를 이걸로 통일해 다시 던진다. `main.py`가 `MainController()` 생성 시점에 이걸 잡아 친절한 메시지 후 종료.
2. `Order.from_dict`/`Sample.from_dict`/`ProductionQueueItem.from_dict`에 숫자 필드 명시적 캐스팅 추가(문자열로 저장된 값도 여기서 걸러지도록).
3. `main.py`에서 `ConsoleView().run()`을 감싸 `EOFError`/`KeyboardInterrupt`를 잡고 정상 종료 메시지 출력.
4. `production_controller.py`의 `tick()`/`get_active_status()`/`get_waiting_queue_status()`가 `OrderNotFoundError`/`SampleNotFoundError`를 만나면 해당 항목을 건너뛰고(활성 항목이면 폐기 후 다음 항목 진행) 계속 동작하도록 수정.
5. `monitoring_controller.inventory_status()`의 `pending_qty` 기준을 `CONFIRMED`(이미 재고에서 선점된 확정 수량 — 0014 이후 재고 부족의 원인이 될 수 없음)에서 `RESERVED`(아직 재고를 확보하지 못한 신규 수요)로 변경.
6. `tools/run_monitor.py`에 `--interval > 0` 검증 추가.
7. `table.py`의 `render_table`에 길이 불일치 시 명확한 `ValueError` 추가.
8. `tools/dummy_data_generator.py`에 `--samples`/`--orders` 음수 검증 추가.

**실행 계획**: 위 8개 항목을 하나씩 구현 → 관련 테스트 추가/보강 → 전체 `pytest` 통과 확인 → PRD.md(4.7 재고 티어 기준) 갱신 → 의미 단위 커밋.

**상태**: ACTION 완료 (8개 항목 전부 수정 + 회귀 테스트 추가, 전체 92개 테스트 통과, 재현 스크립트로 각 수정 사항 수동 재확인). COMMIT 완료 — `f20a833`(데이터 무결성/EOF/Ctrl+C), `f4b7d11`(테스트), `4ecc09b`(생산 큐 참조 방어), `ed5c000`(테스트), `312b1f8`(모니터링 재고 티어), `af4e315`(테스트), `9dd1739`(CLI/table 검증), `79056e7`(테스트).
