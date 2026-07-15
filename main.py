import sys

from sample_order_system.view.console_view import ConsoleView


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")
    ConsoleView().run()


if __name__ == "__main__":
    main()
