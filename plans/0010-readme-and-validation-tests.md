# 0010 — README.md 작성 + 입력 검증 테스트 보강

**날짜**: 2026-07-15

**대상 작업**: 프로젝트 루트 README.md 작성, `SampleController`/`OrderController` 입력 검증 경로에 대한 테스트 추가.

**EXPLORE에서 확인한 사실/제약**:
- 참고 PoC 4개(ConsoleMVC, DataPersistence, DataMonitor, DummyDataGenerator) 모두 README.md로 실행 방법을 안내하지만, SampleOrderSystem에는 CLAUDE.md/PRD.md만 있고 README.md가 없음.
- `sample_controller.py`의 `register_sample`은 이름 공백/생산시간 0 이하/수율 범위 밖에서 `ValueError`를 던지지만 이를 검증하는 테스트가 없음.
- `order_controller.py`의 `create_order`는 수량 0 이하/미등록 시료 ID에서 `ValueError`를 던지지만 이를 검증하는 테스트가 없음.
- 두 항목 모두 "기능 누락"이 아니라 "구현은 됐지만 테스트가 없는 상태".

**실행 계획**:
1. 프로젝트 루트에 `README.md` 작성: 개요, 실행 방법(`python main.py`), 테스트 실행(`pytest`), `tools/` 사용법, 디렉터리 구조, CLAUDE.md/PRD.md로의 링크.
2. `tests/test_input_validation.py` 작성: `register_sample`(빈 이름/생산시간 0 이하/수율 범위 밖 3케이스) + `create_order`(수량 0 이하/미등록 시료 2케이스) 총 5개 테스트.
3. domain-reviewer 관점 리뷰 + spec-guardian 관점 PRD.md 대조.
4. `pytest` 전체 통과 확인 후 커밋.

**상태**: ACTION 완료 (README.md 작성, 검증 테스트 5개 추가, 전체 43개 테스트 통과). COMMIT 완료 — `87c0030`(README), `85bfd6d`(테스트).
