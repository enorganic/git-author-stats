from __future__ import annotations

import argparse
import re
import sys
import warnings
from itertools import islice
from typing import TYPE_CHECKING

from git_author_stats._stats import (
    Stats,
    get_iso_date,
    iter_stats,
    write_stats,
)

if TYPE_CHECKING:
    from collections.abc import Iterable


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
            "repository in CSV/TSV or markdown format"
        ),
        formatter_class=_HelpFormatter,
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
        "-nm",
        "--no-mailmap",
        action="store_true",
        help="Don't use mailmap to map author names to email addresses",
    )
    parser.add_argument(
        "-md",
        "--markdown",
        action="store_true",
        help="Output a markdown table instead of CSV/TSV",
    )
    parser.add_argument(
        "-l",
        "--limit",
        default=0,
        type=int,
        help=(
            "The maximum number of records to return. "
            "The default is 0, indicating there is no limit."
        ),
    )
    parser.add_argument("url", type=str, nargs="+", help="Repository URL(s)")
    namespace: argparse.Namespace = parser.parse_args()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        stats: Iterable[Stats] = iter_stats(
            urls=namespace.url,
            user=namespace.user,
            password=namespace.password,
            since=get_iso_date(namespace.since),
            after=get_iso_date(namespace.after),
            before=get_iso_date(namespace.before),
            until=get_iso_date(namespace.until),
            frequency=namespace.frequency,
            no_mailmap=namespace.no_mailmap,
        )
        if namespace.limit:
            stats = islice(stats, namespace.limit)
        write_stats(
            stats,
            file=sys.stdout,
            delimiter=namespace.delimiter,
            no_header=namespace.no_header,
            markdown=namespace.markdown,
        )


if __name__ == "__main__":
    main()
