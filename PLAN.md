# PLAN.md

> EXPLORE → PLAN → ACTION → COMMIT 진행 로그. **이어쓰기 전용** — 기존 항목을 수정/삭제하지 않고 새 항목을 아래에 추가한다.

---

## 항목 1 — 문서 기반 마련 (CLAUDE.md / PRD.md)

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

**미해결 질문**: 위 4가지 설계 결정 — 항목 2에서 이어서 다룸.

**상태**: COMMIT 완료 (`46018f3`).

---

## 항목 2 — 설계 결정: 재고 차감 시점 확정

**날짜**: 2026-07-15

**대상 작업**: PRD.md 8절 미해결 설계 결정 중 "재고 차감 시점" 확정 및 관련 요구사항 절 수정.

**EXPLORE에서 확인한 사실/제약**:
- 스펙(전체 프로세스 흐름)상 두 경로 모두 최종적으로 `CONFIRMED`를 거쳐 `RELEASE`로 간다.
- 즉시 승인 경로: RESERVED → (재고충분) → CONFIRMED.
- 생산 경로: RESERVED → (재고부족) → PRODUCING → (생산완료) → CONFIRMED.

**결정**: 사용자 확정 — **승인 시점에 재고 차감**. 두 경로에 일관되게 적용하기 위해 "주문이 CONFIRMED로 전환되는 시점에 차감"으로 해석 확정:
- 즉시 승인: 승인 즉시 `stock_quantity -= quantity`.
- 생산 경로: 생산 완료로 실 생산량만큼 재고를 먼저 증가시킨 뒤, 동일 시점에 `quantity`만큼 차감하며 `CONFIRMED`로 전환.
- 출고(`RELEASE`)는 재고에 영향 없음.

**실행 계획**:
1. PRD.md 4.4(주문 승인/거절), 4.5(생산 라인) 절에 차감 로직 반영.
2. PRD.md 8절을 "확정된 결정"과 "미해결"로 분리, 이 결정을 확정 목록으로 이동.

**미해결 질문**: 8.2절의 나머지 3개 항목(초기 재고 입력 여부, 생산 현황 표기 수준, ID 채번 방식)은 계속 미해결.

**상태**: COMMIT 완료 (`46018f3`, 항목 1과 함께 커밋).

---

## 항목 3 — 설계 결정: 초기 재고 입력 여부, ID 채번 방식

**날짜**: 2026-07-15

**대상 작업**: PRD.md 8.2절 미해결 항목 중 2개 확정.

**EXPLORE에서 확인한 사실/제약**:
- 스펙 4항(시료 등록)은 "시료 ID, 이름, 평균 생산시간, 수율"만 등록 속성으로 명시 — stock_quantity, 채번 방식은 언급 없음.

**결정**: 사용자 확정
- 초기 재고: 시료 등록 시 `stock_quantity` 입력받지 않음, 항상 0으로 시작. 이후 생산라인을 통해서만 증가.
- ID 채번: `sample_id`, `order_id` 모두 시스템 자동 증가.

**실행 계획**:
1. PRD.md 4.2(시료 관리), 4.3(주문 접수), 8절 갱신.

**미해결 질문**: 8.2절 잔여 1개 — 생산 현황 표기의 구체적 정보 수준. 이는 설계 결정이라기보다 골격 구현 시 View 단에서 자율적으로 정할 사항이라 판단, 다음 단계(모델/컨트롤러/뷰 골격 EXPLORE→PLAN)로 이월.

**상태**: COMMIT 완료 (`10fbc4e`).

---

## 항목 4 — 확인: 생산 라인은 1개로 고정

**날짜**: 2026-07-15

**대상 작업**: 생산 라인 개수 가정을 PRD.md 3.4절에 명시적으로 반영.

**EXPLORE에서 확인한 사실/제약**:
- 원본 스펙: "하나의 생산 라인은 시료를 하나씩 생산" — 이미 PRD.md 6절(범위 밖)에 "다중 생산 라인 병렬 처리"로 간접 언급되어 있었으나, 도메인 모델(3.4 ProductionQueue) 절에는 명시가 없었음.

**결정**: 사용자 확인 — 생산 라인은 1개. 한 시점에 실제 생산 중인 주문은 최대 1건이며, 나머지 PRODUCING 주문은 FIFO 큐에서 대기.

**실행 계획**:
1. PRD.md 3.4절에 단일 생산 라인 제약을 명시적으로 추가.
2. (다음 단계) ProductionQueue/생산 컨트롤러 골격 설계 시, "현재 생산 중 1건 + 대기 큐" 구조를 기본 전제로 한다.

**상태**: COMMIT 완료 (`f8148ea`).

---

## 항목 5 — Harness: 프로젝트 전용 서브에이전트 4종 스캐폴딩

**날짜**: 2026-07-15

**대상 작업**: `.claude/agents/`에 이 프로젝트 전용 서브에이전트 4종 정의 파일 작성 (spec-guardian, domain-reviewer, test-writer, plan-logger).

**EXPLORE에서 확인한 사실/제약**:
- CLAUDE.md 주안점 2번 "Harness 도입"에 해당하는 반복 가능한 검증 절차로 서브에이전트를 활용하기로 함.
- 아직 소스 코드가 없는 시점이라, 에이전트 정의는 PRD.md/CLAUDE.md/PLAN.md의 규칙(상태 전이 그래프, 재고 차감 시점, 생산량 공식, MVC 의존 방향, EXPLORE→PLAN→ACTION→COMMIT)을 그대로 참조하도록 작성.

**실행 계획**:
1. `.claude/agents/spec-guardian.md` — PRD.md 대비 구현/계획의 스펙 일치 여부 검증.
2. `.claude/agents/domain-reviewer.md` — Clean Code + MVC 의존 방향 + 도메인 룰 위반 검토.
3. `.claude/agents/test-writer.md` — 도메인 로직에 대한 pytest 테스트 작성.
4. `.claude/agents/plan-logger.md` — PLAN.md 항목을 정해진 포맷으로 이어쓰기.

**상태**: ACTION 완료 (`.claude/agents/spec-guardian.md`, `domain-reviewer.md`, `test-writer.md`, `plan-logger.md` 작성, CLAUDE.md에 참조 추가). COMMIT 대기.

---
