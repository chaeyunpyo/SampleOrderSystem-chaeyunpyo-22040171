# 0005 — Harness: 프로젝트 전용 서브에이전트 4종 스캐폴딩

**날짜**: 2026-07-15

**대상 작업**: `.claude/agents/`에 이 프로젝트 전용 서브에이전트 4종 정의 파일 작성 (spec-guardian, domain-reviewer, test-writer, plan-logger).

**EXPLORE에서 확인한 사실/제약**:
- CLAUDE.md 주안점 2번 "Harness 도입"에 해당하는 반복 가능한 검증 절차로 서브에이전트를 활용하기로 함.
- 아직 소스 코드가 없는 시점이라, 에이전트 정의는 PRD.md/CLAUDE.md/plans의 규칙(상태 전이 그래프, 재고 차감 시점, 생산량 공식, MVC 의존 방향, EXPLORE→PLAN→ACTION→COMMIT)을 그대로 참조하도록 작성.

**실행 계획**:
1. `.claude/agents/spec-guardian.md` — PRD.md 대비 구현/계획의 스펙 일치 여부 검증.
2. `.claude/agents/domain-reviewer.md` — Clean Code + MVC 의존 방향 + 도메인 룰 위반 검토.
3. `.claude/agents/test-writer.md` — 도메인 로직에 대한 pytest 테스트 작성.
4. `.claude/agents/plan-logger.md` — plans/ 폴더에 항목을 정해진 포맷으로 추가.

**상태**: COMMIT 완료 (`43d4a8f`).
