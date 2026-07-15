# 0017 — 요약 세로 레이아웃 + 생산 진행률 바 + 시료 목록 정렬 수정

**날짜**: 2026-07-15

**대상 작업**: 사용자 피드백 3건 — (1) 메인 요약("시료 N종 | 총 재고 ... ")을 세로로 정리, (2) 생산 진행률을 progress bar 형태로 표시, (3) "시료 목록 조회"의 열 정렬이 안 맞는 문제 수정.

**EXPLORE에서 확인한 사실**:
- 시료 목록 정렬 문제는 재현해보니 `visible_len`/`pad`의 정렬 계산 자체는 모든 행이 동일한 표시 폭으로 정확히 일치했다 (직접 검증). 실제 원인은 **`avg_production_time`/`yield_rate`를 소수점 자릿수를 고정하지 않고 그대로 문자열화**해서(`0.9` vs `0.95`처럼) 오른쪽 정렬은 되어도 소수점 위치가 안 맞아 보이는 것이었다.
- progress bar는 사용자 확인 결과 생산 진행률에 적용하기로 확정 (요약 화면 수치들은 막대 형태로 바꾸지 않음).

**수정**:
- `table.py`에 `render_bar(percent, width=20)` 추가 — `[███░░░] 42.0%` 형태, 범위 밖 값은 0~100으로 clamp.
- `console_view._print_summary`를 항목당 한 줄씩 세로로 출력하도록 변경.
- `console_view._print_samples`에서 `avg_production_time`은 소수 1자리(`:.1f`), `yield_rate`는 소수 2자리(`:.2f`)로 고정 포맷.
- `console_view._production_menu`의 "현재 생산 중" 표에서 "진행률" 컬럼을 빼고, 표 아래에 `render_bar` 결과를 별도 줄로 표시.

**실행 계획**: table.py에 render_bar 추가 → 테스트 추가 → console_view.py 3곳 수정 → 전체 테스트 통과 확인 → 실제 실행으로 육안 확인 → 커밋.

**상태**: COMMIT 완료 — `37e6a7a`(console_view/table 수정), `314c23d`(테스트).
