# plans/ — EXPLORE → PLAN → ACTION → COMMIT 진행 로그

각 파일은 하나의 작업 단위(사이클)를 기록한다. **번호 순서대로 이어서 추가**하며, 기존 파일의 본문은 수정하지 않는다 (내용이 바뀌면 새 번호로 갱신 사실을 기록). 각 파일의 `**상태**:` 줄만 진행 상황에 따라 갱신 가능하다.

파일명 규칙: `NNNN-짧은-slug.md` (4자리 순번, 이전 항목보다 항상 큰 번호).

| 번호 | 제목 | 날짜 | 상태 |
|---|---|---|---|
| [0001](./0001-docs-setup.md) | 문서 기반 마련 (CLAUDE.md / PRD.md) | 2026-07-15 | COMMIT 완료 (`46018f3`) |
| [0002](./0002-stock-deduction-timing.md) | 설계 결정: 재고 차감 시점 확정 | 2026-07-15 | COMMIT 완료 (`46018f3`) |
| [0003](./0003-initial-stock-and-id-numbering.md) | 설계 결정: 초기 재고 입력 여부, ID 채번 방식 | 2026-07-15 | COMMIT 완료 (`10fbc4e`) |
| [0004](./0004-single-production-line.md) | 확인: 생산 라인은 1개로 고정 | 2026-07-15 | COMMIT 완료 (`f8148ea`) |
| [0005](./0005-harness-subagents.md) | Harness: 프로젝트 전용 서브에이전트 4종 스캐폴딩 | 2026-07-15 | COMMIT 완료 (`43d4a8f`) |
| [0006](./0006-json-persistence-confirmed.md) | 확인: 영속성 방식은 JSON 파일로 확정 | 2026-07-15 | COMMIT 완료 (`45b9328`) |
| [0007](./0007-plan-log-to-folder.md) | PLAN 관리 방식을 단일 파일에서 폴더 구조로 전환 | 2026-07-15 | COMMIT 완료 (`b552584`) |
| [0008](./0008-mvc-skeleton.md) | MVC 골격 구현 (Model/Controller/View + JSON 영속성 + 테스트) | 2026-07-15 | COMMIT 완료 (`9b44691`) |
| [0009](./0009-tools-dummy-data-and-monitor.md) | tools/: 더미데이터 생성기 + 모니터 실행 스크립트 | 2026-07-15 | COMMIT 완료 (`f41f231`) |
| [0010](./0010-readme-and-validation-tests.md) | README.md 작성 + 입력 검증 테스트 보강 | 2026-07-15 | COMMIT 완료 (`85bfd6d`) |
| [0011](./0011-cli-input-usability.md) | CLI 입력 사용성 개선 (재시도 + 취소) | 2026-07-15 | COMMIT 완료 (`eca1702`) |
| [0012](./0012-production-status-detail.md) | 생산 현황 표기 정보량 확대 | 2026-07-15 | COMMIT 완료 (`2eeffa6`) |
| [0013](./0013-cli-color-and-banner.md) | CLI 색상/배너 디자인 추가 | 2026-07-15 | COMMIT 완료 (`1bf52b1`) |
| [0014](./0014-overlapping-order-stock-overcommit-fix.md) | 겹치는 주문/생산 재고 이중 소진 버그 수정 | 2026-07-15 | COMMIT 완료 (`1dbdd3a`) |
| [0015](./0015-cli-table-alignment.md) | CLI 행/열 정렬 및 줄바꿈 사용성 개선 | 2026-07-15 | COMMIT 완료 (`c4bbf48`) |
