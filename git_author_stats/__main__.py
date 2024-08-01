import argparse
import re
import sys
import warnings

from ._stats import get_iso_date, iter_stats, write_stats


class _HelpFormatter(argparse.HelpFormatter):

    def format_help(self) -> str:
        return re.sub(
            r"(\bREGULAR_EXPRESSION_ALIAS\b)([\s\n]+)(\1)",
            r"REGULAR_EXPRESSION\2ALIAS",
            super().format_help(),
        )


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="git-author-stats",
        description=(
            "Print author stats for a Github organization or Git "
            "repository in the format of a Markdown table or CSV/TSV."
        ),
        formatter_class=_HelpFormatter,
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
    parser.add_argument(
        "--since",
        default="",
        type=str,
        help="Only include contributions on or after this date",
    )
    parser.add_argument(
        "--after",
        default="",
        type=str,
        help="Only include contributions after this date",
    )
    parser.add_argument(
        "--before",
        default="",
        type=str,
        help="Only include contributions before this date",
    )
    parser.add_argument(
        "--until",
        default="",
        type=str,
        help="Only include contributions on or before this date",
    )
    parser.add_argument(
        "-f",
        "--frequency",
        default=None,
        type=str,
        help=(
            "If provided, stats will be broken down over time intervals "
            "at the specified frequency. The frequency should be composed of "
            "an integer and unit of time (day, week, month, or year). "
            'For example, all of the following are valid: "1 week", "1w", '
            '"2 weeks", "2weeks", "4 months", or "4m".'
        ),
    )
    parser.add_argument(
        "--delimiter",
        default=",",
        type=str,
        help="The delimiter to use for CSV/TSV output (default: ',')",
    )
    parser.add_argument(
        "-nh",
        "--no-header",
        action="store_true",
        help="Don't print the header row (only applies to CSV/TSV output)",
    )
    parser.add_argument(
        "-md",
        "--markdown",
        action="store_true",
        help="Output a markdown table instead of CSV/TSV",
    )
    parser.add_argument(
        "-rea",
        "--regular-expression-alias",
        default=[],
        action="append",
        nargs=2,
        help=(
            "A regular expression and alias to use when an author "
            "name matches the provided regular expression"
        ),
    )
    parser.add_argument(
        "-e",
        "--email",
        action="store_true",
        help="Include author email addresses in the output",
    )
    parser.add_argument("url", type=str, nargs="+", help="Repository URL(s)")
    namespace: argparse.Namespace = parser.parse_args()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        write_stats(
            iter_stats(
                urls=namespace.url,
                user=namespace.user,
                password=namespace.password,
                since=get_iso_date(namespace.since),
                after=get_iso_date(namespace.after),
                before=get_iso_date(namespace.before),
                until=get_iso_date(namespace.until),
                frequency=namespace.frequency,
                regular_expression_aliases=tuple(
                    namespace.regular_expression_alias
                ),
                email=namespace.email,
            ),
            file=sys.stdout,
            delimiter=namespace.delimiter,
            no_header=namespace.no_header,
            markdown=namespace.markdown,
        )


if __name__ == "__main__":
    main()
