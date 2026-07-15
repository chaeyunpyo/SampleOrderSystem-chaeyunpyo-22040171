# CLAUDE.md

이 파일은 이 저장소(`SampleOrderSystem`)에서 작업하는 Claude Code에 대한 가이드다.

## 프로젝트 개요

반도체 시료 생산주문관리 시스템 — 가상의 반도체 회사 S-Semi를 위한 콘솔 기반 시료/주문/생산/출고 관리 시스템.
전체 기능 요구사항은 [PRD.md](./PRD.md), 원본 스펙은 [개인과제_반도체시료관리.md](./개인과제_반도체시료관리.md) 참고.

이 과제는 **Agentic Engineering 도입**이 주요 평가 대상이다. 코드 자체뿐 아니라 다음 항목의 품질을 함께 갖춰야 한다:

1. CLAUDE.md / PRD.md 등 문서 관리 — 요구사항과 설계 결정을 문서에 먼저 반영하고 코드로 옮긴다.
2. Harness 도입 — 반복 가능한 실행/검증 절차(스크립트, 시드 데이터, 모니터링 도구 등).
3. Test — 핵심 도메인 로직(상태 전이, 생산량 계산, 재고 갱신)은 자동화 테스트로 검증한다.
4. Clean Code — 단일 책임, 명확한 네이밍, 불필요한 추상화 지양.
5. Commit 이력 — 의미 단위로 나뉜 커밋. 하나의 커밋에 여러 관심사를 섞지 않는다.

## 작업 범위

- 이 폴더(`SampleOrderSystem-chaeyunpyo-22040171`) 내부만 수정한다.
- 상위 `C:\reviewer\mission` 안의 `ConsoleMVC`, `DataPersistence`, `DataMonitor`, `DummyDataGenerator`는 동일 스펙을 다룬 **이전 PoC이자 참조 자료**다. 패턴을 참고하되 그 폴더들을 직접 수정하지 않는다.

## 아키텍처

`ConsoleMVC` PoC의 계층 분리를 기준으로 확장한다.

```
sample_order_system/
├── model/          # 도메인 엔티티(Sample, Order), 상태 Enum, Repository(영속성)
├── controller/     # 메뉴별 흐름 제어 및 상태 전이 로직
│   ├── main_controller.py
│   ├── sample_controller.py
│   ├── order_controller.py
│   ├── monitoring_controller.py
│   ├── production_controller.py
│   └── shipping_controller.py
└── view/           # 콘솔 입출력 전담 (비즈니스 로직 없음)
main.py             # 실행 진입점
tools/               # 더미 데이터 생성기, 모니터링 실행 스크립트 등 harness
tests/               # pytest 테스트
data/                # 실행 시 생성되는 JSON 데이터 파일 (git 미추적)
```

의존 방향: `View → Controller → Model` (역방향 의존 금지). Model은 Controller/View를 모른다.

## 기술 스택

- Python 3.9+, 표준 라이브러리 우선 (이전 PoC들과 동일하게 외부 의존성 최소화).
- 영속성: JSON 파일 (`data/samples.json`, `data/orders.json` 등). DB 연동 없음.
- 테스트: `pytest`.

## 도메인 규칙 요약 (상세는 PRD.md 참고)

- 주문 상태: `RESERVED → (REJECTED | CONFIRMED | PRODUCING) → CONFIRMED → RELEASE`. 역방향 전이 없음. `REJECTED`/`RELEASE`는 종단 상태.
- 승인 시 재고 충분 여부로 `CONFIRMED`/`PRODUCING` 자동 분기.
- 생산량 계산: 실 생산량 = `ceil(부족분 / yield_rate)`, 총 생산 시간 = `avg_production_time * 실 생산량`.
- 생산 큐는 FIFO.
- 모니터링에서 `REJECTED`는 항상 제외.
- 재고 상태 3단계: 여유 / 부족 / 고갈 (기준은 PRD.md 4.7 참고).

구현 중 스펙에 없는 세부사항(재고 차감 시점, ID 채번 방식 등)을 결정할 때는 PRD.md의 "미해결 설계 결정" 절에 먼저 기록하고 진행한다.

## 개발 워크플로

1. 기능 착수 전, 해당 기능이 PRD.md의 요구사항과 일치하는지 확인한다. 요구사항이 모호하면 PRD.md를 먼저 갱신한다.
2. Model → Controller → View 순으로 구현하고, Model 로직은 View/Controller 없이 단위 테스트 가능해야 한다.
3. 상태 전이·계산 로직을 작성/변경할 때마다 대응하는 테스트를 함께 작성한다.
4. 커밋은 기능/계층 단위로 분리한다 (예: "Sample 모델 추가", "주문 승인 시 재고 분기 로직 구현").

## 개발 프로세스: EXPLORE → PLAN → ACTION → COMMIT

모든 작업 단위(기능/이슈/리팩터링)는 아래 4단계를 순서대로 거친다.

1. **EXPLORE** — 관련 스펙(PRD.md, 개인과제_반도체시료관리.md), 기존 코드, 참고 PoC를 먼저 읽고 이해한다. 코드를 작성하지 않는다.
2. **PLAN** — 진행에 앞서 반드시 [PLAN.md](./PLAN.md)에 새 항목을 추가한다. 기존 내용은 지우거나 덮어쓰지 않고 이어서 기록한다(append-only 로그). 각 항목에는 다음을 포함한다: 날짜, 대상 작업, EXPLORE에서 확인한 사실/제약, 실행 계획(단계별), 미해결 질문(있는 경우).
3. **ACTION** — PLAN.md에 적은 계획대로 구현한다. 계획과 다르게 진행해야 하면 먼저 PLAN.md의 해당 항목을 갱신(추가 기록)한 뒤 진행한다.
4. **COMMIT** — 작업 단위가 끝나면 의미 단위로 커밋한다. 커밋 메시지는 PLAN.md 항목의 "대상 작업"과 대응되게 작성한다.

즉, **PLAN 단계 진입 시 PLAN.md 갱신이 선행 조건**이다. PLAN.md 없이 ACTION으로 넘어가지 않는다.

## 명령어

> 아래는 프로젝트 구조 확정 후 갱신 예정. 초기 골격 작성 시 실제 명령으로 교체할 것.

```bash
python main.py          # 콘솔 앱 실행
pytest                  # 테스트 실행
python tools/dummy_data_generator.py --samples N --orders N   # 더미 데이터 생성 (예정)
python tools/run_monitor.py                                   # 모니터링 도구 실행 (예정)
```
