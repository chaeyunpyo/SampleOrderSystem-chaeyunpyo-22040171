import sys

from sample_order_system.view.colors import enable_windows_ansi
from sample_order_system.view.console_view import ConsoleView


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")
    enable_windows_ansi()
    ConsoleView().run()


if __name__ == "__main__":
    main()
