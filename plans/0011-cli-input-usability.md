# 0011 — CLI 입력 사용성 개선 (재시도 + 취소)

**날짜**: 2026-07-15

**대상 작업**: `console_view.py`의 다단계 입력 흐름(시료 등록/주문 접수/승인·거절/출고)에서 잘못된 입력을 입력하면 흐름 전체가 취소되고 메뉴로 돌아가던 문제를 개선. 잘못된 값은 같은 항목만 재입력받고, 빈 입력(Enter)으로 언제든 현재 작업을 취소할 수 있게 한다.

**EXPLORE에서 확인한 사실/제약**:
- 현재 `_register_sample`, `_create_order`, `_approve_or_reject_order`, `_shipping_menu`는 각 입력을 한 번씩만 받고 `int()`/`float()` 변환 실패나 컨트롤러의 `ValueError`를 하나의 `try/except`로 묶어 처리한다. 숫자 하나만 잘못 입력해도 등록/접수 전체가 취소되고 서브메뉴로 돌아간다(ConsoleMVC PoC도 동일한 구조였음 — 이 프로젝트에서 개선 대상으로 삼음).
- 진행 중인 입력 시퀀스를 사용자가 스스로 취소할 방법이 없다 (예: 시료 이름을 입력한 뒤 생각이 바뀌어도 끝까지 입력해야 함).
- 컨트롤러 계층(검증 로직)은 이미 완성되어 있어 View 계층만 수정하면 된다 — MVC 의존 방향에 영향 없음.

**설계**:
- `console_view.py`에 입력 헬퍼 3종 추가: `_read_required(prompt) -> str | None`, `_read_int(prompt) -> int | None`, `_read_float(prompt) -> float | None`.
  - 빈 입력(Enter만 입력) → 즉시 `None` 반환(취소)하고 안내 문구 없이 호출부에서 "취소되었습니다." 출력.
  - 숫자 변환 실패 → "숫자를 입력하세요. (취소하려면 Enter)" 출력 후 같은 프롬프트 재출력 (전체 흐름 재시작 아님).
- `_register_sample`, `_create_order`, `_approve_or_reject_order`, `_shipping_menu`을 위 헬퍼로 재작성. 컨트롤러 호출까지 도달한 뒤 발생하는 `ValueError`(비즈니스 규칙 위반)는 기존처럼 인라인 출력하되, 흐름을 처음부터 다시 타지 않고 서브메뉴로 자연스럽게 복귀.

**실행 계획**:
1. `console_view.py`에 `_read_required`/`_read_int`/`_read_float` 헬퍼 추가.
2. 4개 입력 흐름(`_register_sample`, `_create_order`, `_approve_or_reject_order`, `_shipping_menu`)을 헬퍼 기반으로 재작성.
3. `tests/test_console_view_prompts.py` — `builtins.input`을 monkeypatch하여 헬퍼 3종의 재시도/취소 동작 검증.
4. domain-reviewer 관점 리뷰(View에 비즈니스 로직 유입 여부 확인), spec-guardian 관점 확인(PRD 기능 변경 없음, UX만 개선이므로 상충 없음).
5. `pytest` 전체 통과 확인 후 커밋.

**상태**: ACTION 완료 (`_read_required`/`_read_int`/`_read_float` 헬퍼 추가, 4개 입력 흐름 재작성, 테스트 6개 추가, 전체 49개 테스트 통과, `python main.py`로 재시도/취소 동작 수동 확인). COMMIT 완료 — `1fd19f1`(console_view.py), `eca1702`(테스트).
