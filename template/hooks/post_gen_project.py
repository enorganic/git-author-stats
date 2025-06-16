from contextlib import suppress
from subprocess import check_call


def main() -> None:
    with suppress(Exception):
        check_call(("make",))
        check_call(("make", "format"))


if __name__ == "__main__":
    main()
