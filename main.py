import sys

from sample_order_system.model.errors import DataIntegrityError
from sample_order_system.view.colors import enable_windows_ansi
from sample_order_system.view.console_view import ConsoleView


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")
    enable_windows_ansi()

    try:
        view = ConsoleView()
    except DataIntegrityError as e:
        print(f"데이터 파일에 문제가 있어 앱을 시작할 수 없습니다: {e}")
        sys.exit(1)

    try:
        view.run()
    except EOFError:
        print("\n입력이 종료되어 프로그램을 종료합니다.")
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")


if __name__ == "__main__":
    main()
