# 0015 — CLI 행/열 정렬 및 줄바꿈 사용성 개선

**날짜**: 2026-07-15

**대상 작업**: 시료/주문 목록, 모니터링, 생산 라인 대기 큐 출력을 열 정렬된 표 형태로 개선. 섹션 간 줄바꿈 간격도 일관되게 정리.

**EXPLORE에서 확인한 사실/제약**:
- 현재 출력은 `"|"`로 구분된 한 줄 문자열이라 항목마다 길이가 달라 열이 맞지 않는다.
- 0013에서 넣은 ANSI 색상 코드는 터미널에서는 안 보이지만 파이썬 문자열 길이에는 포함되므로, `str.ljust`/`rjust`를 색상 적용 후 텍스트에 바로 쓰면 색상 이스케이프 코드 길이만큼 정렬이 깨진다. → ANSI 코드를 무시하고 "보이는 길이"만 계산하는 정렬 유틸리티가 필요.

**설계**:
- `sample_order_system/view/table.py` 신규: `visible_len(text)`(ANSI 이스케이프 제거 후 길이), `pad(text, width, align)`(보이는 길이 기준 패딩, 색상 적용된 텍스트도 안전), `render_table(headers, rows, aligns=None) -> list[str]`(헤더/구분선/행을 정렬된 문자열 리스트로 반환).
- `console_view.py`의 아래 출력을 표로 전환:
  - `_print_samples`: ID/이름/생산시간/수율/재고
  - 주문 목록(RESERVED 승인·거절 화면, CONFIRMED 출고 화면): ID/시료/고객/수량
  - `_monitoring_menu`: 상태별 건수·수량 표, 재고 현황 표
  - `_production_menu`의 대기 큐: #/주문/시료/고객/주문수량/부족분/실생산량/소요(분)/대기(분)
- 색상은 각 셀의 텍스트 폭 계산 후(또는 무관하게 `visible_len` 기준으로) 적용해도 정렬이 깨지지 않도록 셀 값을 만들 때 색상 적용 → `render_table`에 전달하는 순서로 통일.
- 섹션 간 줄바꿈: 각 서브메뉴 출력 앞뒤로 빈 줄 1개씩 일관되게, 표 위아래에도 여백 추가.

**실행 계획**:
1. `sample_order_system/view/table.py` 작성.
2. `tests/test_table.py` — `visible_len`/`pad`/`render_table`가 색상 코드 포함 텍스트에도 정확한 폭으로 정렬하는지 검증.
3. `console_view.py`의 5개 출력 지점을 표 렌더링으로 교체, 줄바꿈 간격 정리.
4. `pytest` 전체 통과 확인, `python main.py` 실행으로 실제 정렬 상태 육안 확인.
5. domain-reviewer 관점 리뷰(View 전용 순수 표현 로직인지 확인), 커밋.

**상태**: ACTION 완료 (`table.py` 신규 — ANSI 무시 + 한글 등 동아시아 넓은 문자 2칸 폭 반영, `console_view.py`의 5개 출력 지점을 표로 전환 + 줄바꿈 간격 정리, 테스트 10개 추가, 전체 71개 테스트 통과, 실제 실행으로 정렬 확인). COMMIT 완료 — `1c3c212`(table.py), `3de5168`(테스트), `c4bbf48`(console_view.py 적용).
