# 0001 — 문서 기반 마련 (CLAUDE.md / PRD.md)

**날짜**: 2026-07-15

**대상 작업**: 프로젝트 문서 체계 수립 (CLAUDE.md, PRD.md)

**EXPLORE에서 확인한 사실/제약**:
- 원본 스펙(`개인과제_반도체시료관리.md`)은 `SampleOrderSystem-chaeyunpyo-22040171` 폴더 내부에 위치.
- 작업 범위는 `SampleOrderSystem` 폴더로 한정, 나머지 형제 폴더(ConsoleMVC, DataPersistence, DataMonitor, DummyDataGenerator)는 동일 스펙을 다룬 참조 전용 PoC.
- 4개 PoC가 각각 스펙의 한 부분을 구현: ConsoleMVC(MVC 골격, 시료관리+주문 접수/승인/거절), DataPersistence(JSON CRUD 영속성), DataMonitor(콘솔 모니터링+시뮬레이터), DummyDataGenerator(더미 시료/주문 생성).
- 공통 스택: Python 3.x, 표준 라이브러리 위주, JSON 파일을 DB 대체로 사용, 콘솔 CLI.
- ConsoleMVC는 pytest 사용, DataPersistence는 unittest 사용 — 통일 필요.

**실행 계획**:
1. PRD.md 작성 — 스펙을 기능 요구사항/도메인 모델/상태 흐름/비기능 요구사항으로 재구성.
2. CLAUDE.md 작성 — 작업 범위, 아키텍처(MVC), 기술 스택, 도메인 규칙 요약, 개발 워크플로 명시.
3. 미해결 설계 결정을 PRD.md 8절에 기록 (재고 차감 시점, 초기 재고 입력 여부, 생산 현황 표기 수준, ID 채번 방식).

**미해결 질문**: 위 4가지 설계 결정 — [0002](./0002-stock-deduction-timing.md)부터 이어서 다룸.

**상태**: COMMIT 완료 (`46018f3`).
