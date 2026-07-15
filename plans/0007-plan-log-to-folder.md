# 0007 — PLAN 관리 방식을 단일 파일에서 폴더 구조로 전환

**날짜**: 2026-07-15

**대상 작업**: `PLAN.md` 단일 이어쓰기 파일을 `plans/NNNN-slug.md` 형태의 폴더 구조로 전환.

**EXPLORE에서 확인한 사실/제약**:
- 기존 `PLAN.md`는 항목 1~6이 누적되며 파일이 길어져 가독성이 떨어짐.
- 사용자 요청: 한 파일보다 폴더 내 순서대로 관리하는 편이 보기 편함.

**결정**: 사용자 확정 — `plans/` 폴더에 항목별 파일(`0001-...` ~ )로 분리하고, `plans/README.md`를 인덱스(번호/제목/날짜/상태 표)로 둔다. append-only 원칙은 유지하되 "이어쓰기"가 "새 번호 파일 추가"로 바뀐다.

**실행 계획**:
1. 기존 PLAN.md 항목 1~6을 각각 `plans/0001-*.md` ~ `plans/0006-*.md`로 그대로 이관 (내용 변경 없이 형식만 분리, 상호 참조 링크 추가).
2. `plans/README.md` 인덱스 작성.
3. 이 전환 작업 자체를 `plans/0007-plan-log-to-folder.md`로 기록.
4. 루트의 `PLAN.md` 삭제.
5. `CLAUDE.md`에서 `PLAN.md` 참조를 `plans/` 폴더 참조로 수정.
6. `.claude/agents/plan-logger.md`를 새 폴더 구조 기준으로 재작성 (항목 추가 = 새 파일 생성 + README.md 인덱스 갱신).

**상태**: ACTION 완료 (PLAN.md → plans/0001~0006 이관, README.md 인덱스 작성, CLAUDE.md/spec-guardian/plan-logger 참조 갱신, PLAN.md 삭제). COMMIT 대기.
