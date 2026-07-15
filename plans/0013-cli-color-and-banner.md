# 0013 — CLI 색상/배너 디자인 추가

**날짜**: 2026-07-15

**대상 작업**: 콘솔 UI에 상태/결과 중심 채색과 시작 화면 ASCII 아트 배너 추가. 사용자가 "색상 사용, 보기 편한 UI, 귀여운 그림"을 요청.

**EXPLORE에서 확인한 사실/제약**:
- 표준 라이브러리만 사용하는 기존 원칙(CLAUDE.md 기술 스택)을 유지하기 위해 `colorama` 등 외부 패키지 대신, Windows에서 ANSI 이스케이프를 활성화하는 `ctypes` 기반 `SetConsoleMode` 호출(표준 라이브러리)로 처리한다. `main.py`가 이미 `sys.stdout.reconfigure(encoding="utf-8")`로 UTF-8을 강제하고 있어 박스 문자/이모지 렌더링에는 문제 없음.
- 색상 적용 범위는 사용자가 "상태/결과 중심"으로 확정: 주문 상태(RESERVED/CONFIRMED/PRODUCING/RELEASE/REJECTED), 재고 티어(여유/부족/고갈), 성공/실패/취소 메시지.
- ASCII 아트는 앱 시작 시 1회 배너로 표시하기로 확정.

**설계**:
- `sample_order_system/view/colors.py` 신규: ANSI 색상 상수, `colorize()`, `enable_windows_ansi()`(Windows에서만 동작, 실패해도 조용히 무시), `status_text(status)`(상태별 색), `tier_text(tier)`(재고 티어별 색), `success()`/`failure()`/`muted()` 헬퍼.
- `console_view.py`: 주문 상태 출력, 재고 티어 출력, 등록/접수/승인/거절/출고/생산완료 성공 메시지, `실패`/`취소되었습니다` 메시지에 색상 적용. `run()` 시작 시 1회 ASCII 아트 배너 출력.
- `main.py`: 실행 시작 시 `enable_windows_ansi()` 호출.

**실행 계획**:
1. `sample_order_system/view/colors.py` 작성.
2. `console_view.py`에 배너 출력 + 색상 적용 반영.
3. `main.py`에 `enable_windows_ansi()` 호출 추가.
4. `tests/test_colors.py` — 색상 매핑/헬퍼 동작 검증 (ANSI 코드 포함 여부).
5. domain-reviewer 관점 리뷰(View 계층에만 색상 로직 존재, Model/Controller 무관 확인), spec-guardian 관점 확인(PRD 기능 변경 없음, UX 개선이라 상충 없음).
6. `pytest` 전체 통과 확인, 실제 실행으로 시각 확인 후 커밋.

**상태**: ACTION 완료 (`colors.py` 신규, `console_view.py`/`main.py`에 색상+배너 적용, 테스트 6개 추가, 전체 59개 테스트 통과, `python main.py` 실행으로 배너/색상 육안 확인). COMMIT 완료 — `1309ce6`(colors.py+main.py), `7228fab`(console_view.py 적용), `1bf52b1`(테스트).
