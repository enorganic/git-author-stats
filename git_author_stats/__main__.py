import argparse

from ._stats import clone


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="git-author-stats",
        description=(
            "Retrieve author stats for a Github organization or Git "
            "repository."
        ),
    )
    parser.add_argument(
        "-b",
        "--branch",
        default="",
        type=str,
        help="Retrieve files from BRANCH instead of the remote's HEAD",
    )
    parser.add_argument(
        "-u",
        "--user",
        default="",
        type=str,
        help="A username for accessing the repository",
    )
    parser.add_argument(
        "-p",
        "--password",
        default="",
        type=str,
        help="A password for accessing the repository",
    )
    parser.add_argument("url", type=str, nargs="+", help="Repository URL(s)")
    namespace: argparse.Namespace = parser.parse_args()
    clone(
        namespace.url,
        user=namespace.user,
        password=namespace.password,
    )


if __name__ == "__main__":
    main()
