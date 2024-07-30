import argparse
import csv
import sys
import warnings
from dataclasses import Field, fields
from datetime import date
from typing import Any, List, Tuple, Union

from ._stats import Stats, get_iso_date, iter_stats


def _get_string_value(value: Union[str, date, float, int, None]) -> str:
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def print_markdown_table(rows: List[Tuple[str, ...]]) -> None:
    """
    Print a Markdown table representation of a list of equal-length tuples.

    Parameters:

    - rows (List[Tuple[str, ...]): The rows in the table.
    """
    if not rows:
        return
    index: int
    row: Tuple[str, ...]
    indices: Tuple[int, ...] = tuple(range(len(rows[0])))
    column_widths: Tuple[int, ...] = tuple(
        map(lambda index: max(map(lambda row: len(row[index]), rows)), indices)
    )
    empty_value: str = " " * max(column_widths)
    is_first: bool = True
    for row in rows:
        value: str
        print(
            "| {} |".format(
                " | ".join(
                    f"{value}{empty_value}"[: column_widths[index]]
                    for index, value in zip(indices, row)
                )
            )
        )
        if is_first:
            # Print the header separator
            print(
                "| {} |".format(
                    " | ".join("-" * column_widths[index] for index in indices)
                )
            )
        is_first = False


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="git-author-stats",
        description=(
            "Print author stats for a Github organization or Git "
            "repository in the format of a Markdown table or CSV/TSV."
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
        default="",
        type=str,
        help=(
            "If provided, the output will be a CSV-like table with the "
            "specified delimiter. If not provided, the output will be a "
            "Markdown table."
        ),
    )
    parser.add_argument("url", type=str, nargs="+", help="Repository URL(s)")
    namespace: argparse.Namespace = parser.parse_args()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        field: Field
        # Print the header
        field_names: Tuple[str, ...] = tuple(
            map(lambda field: field.name, fields(Stats))
        )
        rows: List[Tuple[str, ...]] = []
        stdout_csv_writer: Any
        if namespace.delimiter:
            stdout_csv_writer = csv.writer(
                sys.stdout,
                delimiter=namespace.delimiter,
                lineterminator="\n",
            )
            stdout_csv_writer.writerow(field_names)
        else:
            rows.append(field_names)
        stats: Stats
        for stats in iter_stats(
            urls=namespace.url,
            user=namespace.user,
            password=namespace.password,
            since=get_iso_date(namespace.since),
            after=get_iso_date(namespace.after),
            before=get_iso_date(namespace.before),
            until=get_iso_date(namespace.until),
            frequency=namespace.frequency,
        ):
            row: Tuple[str, ...] = tuple(
                map(
                    _get_string_value,
                    map(stats.__getattribute__, field_names),
                )
            )
            if namespace.delimiter:
                stdout_csv_writer.writerow(row)
            else:
                rows.append(row)
        if rows:
            print_markdown_table(rows)


if __name__ == "__main__":
    main()
