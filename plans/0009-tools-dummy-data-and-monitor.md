# 0009 — tools/: 더미데이터 생성기 + 모니터 실행 스크립트

**날짜**: 2026-07-15

**대상 작업**: [0008](./0008-mvc-skeleton.md)에서 분리해둔 `tools/`(더미데이터 생성기, 모니터 스크립트) 구현.

**EXPLORE에서 확인한 사실/제약**:
- DummyDataGenerator PoC(참조 전용, `C:\reviewer\mission\DummyDataGenerator-chaeyunpyo-22040171\dummy_data_generator.py`): `--samples/--orders/--reset` argparse, `--reset` 없으면 기존 데이터에 이어서 추가(ID는 max+1부터), 상태는 5개 값 중 균등 무작위(REJECTED 포함), JSON은 비원자적 `write_text` 저장.
- DataMonitor PoC(참조 전용, `C:\reviewer\mission\DataMonitor-chaeyunpyo-22040171\src\data_monitor\{store,monitor}.py`): `store.py`가 원자적 저장(temp+`os.replace`)과 상태별 건수/재고 티어 집계를 직접 구현하고, `monitor.py`가 `--interval`/`--once`로 폴링하며 화면을 지우고(`os.system("cls"/"clear")`) 다시 그리는 루프.
- 두 PoC 모두 자체 JSON 스키마/집계 로직을 처음부터 재구현했지만, 이 프로젝트는 이미 `SampleRepository`/`OrderRepository`(원자적 저장, S/O 자동채번)와 `MonitoringController`(상태별 건수+수량, 재고 티어)를 갖고 있으므로 **재구현하지 않고 그대로 재사용**한다 — Clean Code 원칙(중복 방지)에 부합.

**설계 결정**:
- `tools/dummy_data_generator.py`: `SampleRepository`/`OrderRepository`를 그대로 사용해 더미 시료/주문을 생성. `--samples N`(기본 10), `--orders M`(기본 20), `--reset`(기존 `data/samples.json`/`orders.json`/`production_state.json` 삭제 후 새로 생성) 플래그. `--reset` 없으면 기존 데이터에 이어서 추가(리포지토리의 `next_id()`가 자동으로 이어서 채번).
  - 더미 시료는 `SampleController.register_sample`을 거치지 않고 `Sample`을 직접 생성해 `stock_quantity`도 무작위로 채운다 — 이는 데모/테스트 데이터를 즉시 그럴듯하게 보이게 하려는 도구의 의도적 예외이며, 실제 앱 사용자 흐름(등록 시 재고 0 시작)과는 무관함을 PRD에 명시한다.
  - 더미 주문의 상태는 `RESERVED`/`REJECTED`/`CONFIRMED`/`RELEASE` 중에서만 무작위 배정한다(`PRODUCING`은 제외) — `PRODUCING`은 `production_state.json`의 큐/활성 항목과 반드시 짝을 이뤄야 하는데, 더미 생성기가 임의로 `PRODUCING` 주문만 만들면 생산 큐 파일과 불일치하는 상태가 되어 앱 로직(FIFO 큐, 진행률 표시)이 깨지기 때문.
- `tools/run_monitor.py`: `SampleRepository`/`OrderRepository`/`MonitoringController`를 그대로 사용. `--interval`(기본 2.0초), `--once`, `--data-dir`(기본 `data/`) 플래그. 매 폴링마다 리포지토리를 새로 생성해(파일 재로드) 최신 상태 반영, 화면 클리어 후 상태별 건수/수량 + 재고 티어 표를 렌더링.

**실행 계획**:
1. `tools/dummy_data_generator.py` 작성 (argparse, 이름/고객명 풀, 랜덤 필드 생성, reset 처리).
2. `tools/run_monitor.py` 작성 (polling 루프, 콘솔 렌더링).
3. `tests/test_dummy_data_generator.py` — 생성 개수, reset 여부에 따른 누적/초기화, ID 이어채번 검증.
4. domain-reviewer 관점 리뷰, spec-guardian 관점 PRD.md 대조.
5. PRD.md 5절(Dummy Data, 모니터링 도구 항목)에 구체적 사용법 반영.

**상태**: ACTION 완료 (`tools/dummy_data_generator.py`, `tools/run_monitor.py`, `tests/test_dummy_data_generator.py`, 전체 38개 테스트 통과, PRD.md/CLAUDE.md 사용법 반영). 스모크 테스트 중 `os.replace`의 Windows 일시적 파일 잠금(PermissionError) 발견 → `json_store.py`에 재시도 로직 추가로 별도 수정. COMMIT 완료 — `3f95582`(원자적 쓰기 재시도), `f41f231`(tools/ 구현+테스트).
