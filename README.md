# SampleOrderSystem

반도체 시료 생산주문관리 시스템 — 가상의 반도체 회사 **S-Semi**를 위한 콘솔 기반 시료/주문/생산/출고 관리 애플리케이션.

전체 기능 명세는 [PRD.md](./PRD.md), 원본 과제 스펙은 [개인과제_반도체시료관리.md](./개인과제_반도체시료관리.md), 개발 워크플로와 아키텍처 규칙은 [CLAUDE.md](./CLAUDE.md)를 참고한다. 진행 이력은 [plans/](./plans/README.md)에 EXPLORE→PLAN→ACTION→COMMIT 단위로 기록되어 있다.

## 요구 사항

- Python 3.9+ (표준 라이브러리만 사용, 앱 실행에 외부 의존성 없음)
- 테스트 실행에는 `pytest`가 필요 (`requirements-dev.txt` 참고)

## 설치

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements-dev.txt
```

## 실행

```bash
python main.py
```

콘솔 메뉴에서 번호를 입력해 시료 관리 / 주문(접수·승인·거절) / 모니터링 / 출고 처리 / 생산 라인을 조작한다. 데이터는 `data/`에 JSON 파일(`samples.json`, `orders.json`, `production_state.json`)로 저장되며, 앱을 종료 후 다시 실행해도 그대로 복원된다 (`data/`는 git에 커밋되지 않음).

생산 완료는 실제 sleep 없이 Mock Clock(`SystemClock`) 방식으로 처리된다 — 메뉴를 렌더링할 때마다 "생산 시작 후 경과한 실제 시간"이 해당 시료의 총 생산 시간을 넘었는지 확인해 자동으로 완료 처리한다.

## 테스트

```bash
pytest
```

상태 전이, 재고 차감 시점, 생산량/생산시간 공식, FIFO 단일 생산 라인, 재고 상태 판정, 모니터링 집계, JSON 영속성, ID 자동 채번, 입력 검증 등 도메인 로직 전반을 다룬다.

## 보조 도구 (`tools/`)

```bash
python -m tools.dummy_data_generator --samples 10 --orders 20 [--reset]   # 더미 시료/주문 생성
python -m tools.run_monitor --interval 2 [--once]                        # 콘솔 모니터링 도구
```

두 스크립트 모두 앱 본체와 동일한 리포지토리/컨트롤러(`SampleRepository`, `OrderRepository`, `MonitoringController`)를 재사용하므로, 실제 `data/` 파일을 그대로 읽고 쓴다. `tools/*.py`는 `sample_order_system` 패키지를 import하므로 프로젝트 루트에서 `python -m tools.xxx` 형태로 실행해야 한다.

## 디렉터리 구조

```
sample_order_system/
├── model/          # 도메인 엔티티, Clock, JSON 리포지토리
├── controller/      # 메뉴별 흐름 제어 및 상태 전이 로직
└── view/            # 콘솔 입출력 (console_view.py)
main.py              # 실행 진입점
tools/                # 더미데이터 생성기, 모니터 실행 스크립트
tests/                # pytest 테스트
data/                 # 실행 시 생성되는 JSON 데이터 (git 미추적)
plans/                # EXPLORE→PLAN→ACTION→COMMIT 진행 로그
```

의존 방향은 `View → Controller → Model` 단방향이다.
