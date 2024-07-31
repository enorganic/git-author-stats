import sys
from datetime import date, timedelta
from io import StringIO
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

import pandas  # type: ignore
import polars
import pytest

from git_author_stats._stats import (
    Frequency,
    FrequencyUnit,
    Stats,
    check_output,
    get_first_author_date,
    increment_date_by_frequency,
    iter_date_ranges,
    iter_stats,
    parse_frequency_string,
    read_stats,
    write_stats,
)

ROOT_PATH: Path = Path(__file__).absolute().parent.parent
STATS_CSV_PATH: Path = ROOT_PATH / "tests/stats.csv"
STATS_TSV_PATH: Path = ROOT_PATH / "tests/stats.tsv"
STATS_MD_PATH: Path = ROOT_PATH / "tests/stats.md"


def test_parse_frequency_string() -> None:
    assert parse_frequency_string("1 week") == Frequency(1, FrequencyUnit.WEEK)
    assert parse_frequency_string("1w") == Frequency(1, FrequencyUnit.WEEK)
    assert parse_frequency_string("365d") == Frequency(365, FrequencyUnit.DAY)
    assert parse_frequency_string("2y") == Frequency(2, FrequencyUnit.YEAR)
    assert parse_frequency_string("2 YEARS") == Frequency(
        2, FrequencyUnit.YEAR
    )
    assert parse_frequency_string("week") == Frequency(1, FrequencyUnit.WEEK)


def test_increment_date_by_frequency() -> None:
    assert increment_date_by_frequency(
        date(2020, 1, 1),
        frequency=Frequency(1, FrequencyUnit.WEEK),
    ) == date(2020, 1, 8)
    assert increment_date_by_frequency(
        date(2020, 1, 1),
        frequency=Frequency(1, FrequencyUnit.MONTH),
    ) == date(2020, 2, 1)
    # Next year, and for a shorter month
    assert increment_date_by_frequency(
        date(2020, 12, 31),
        frequency=Frequency(2, FrequencyUnit.MONTH),
    ) == date(2021, 2, 28)
    # January -> December
    assert increment_date_by_frequency(
        date(2020, 1, 1), Frequency(quantity=11, unit=FrequencyUnit.MONTH)
    ) == date(2020, 12, 1)


def test_iter_date_ranges() -> None:
    period_since: Optional[date]
    period_before: Optional[date]
    since: date = date(2020, 1, 1)
    before: date = date(2022, 9, 30)
    # Weekly
    for period_since, period_before in iter_date_ranges(
        since=since,
        before=before,
        frequency=Frequency(1, FrequencyUnit.WEEK),
    ):
        assert period_since and period_before
        assert period_before == min(before, period_since + timedelta(days=7))
    # Bi-Weekly
    for period_since, period_before in iter_date_ranges(
        since=since,
        before=before,
        frequency=Frequency(2, FrequencyUnit.WEEK),
    ):
        assert period_since and period_before
        assert period_before == min(before, period_since + timedelta(days=14))
    # Monthly
    for period_since, period_before in iter_date_ranges(
        since=since,
        before=before,
        frequency=Frequency(1, FrequencyUnit.MONTH),
    ):
        assert period_since and period_before
        assert (
            timedelta(days=31)
            >= (period_before - period_since)
            >= timedelta(days=28)
        ) or period_before == before, f"{period_since} -> {period_before}"
    # Bi-Monthly
    for period_since, period_before in iter_date_ranges(
        since=since,
        before=before,
        frequency=Frequency(2, FrequencyUnit.MONTH),
    ):
        assert period_since and period_before
        assert (
            timedelta(days=62)
            >= (period_before - period_since)
            >= timedelta(days=58)
        ) or period_before == before, f"{period_since} -> {period_before}"


def test_iter_repo_stats() -> None:
    """
    Test creating a pandas data frame from the stats of a single repository.
    """
    stats: Tuple[Stats, ...] = tuple(
        iter_stats(
            urls="https://github.com/enorganic/git-author-stats.git",
            frequency=Frequency(2, FrequencyUnit.WEEK),
            since=date.today() - timedelta(days=365),
        )
    )
    assert stats
    pandas_data_frame: pandas.DataFrame = pandas.DataFrame(stats)
    assert pandas_data_frame.columns.tolist() == [
        "url",
        "author",
        "since",
        "before",
        "insertions",
        "deletions",
        "file",
    ], stats
    polars_data_frame: polars.DataFrame = polars.DataFrame(stats)
    assert polars_data_frame.columns == [
        "url",
        "author",
        "since",
        "before",
        "insertions",
        "deletions",
        "file",
    ], stats


def test_get_first_author_date() -> None:
    """
    Test getting the first author date using this repository.
    """
    assert get_first_author_date(ROOT_PATH) >= date(2024, 4, 30)


def test_cli() -> None:
    # Markdown
    lines: List[str] = (
        check_output(
            (
                sys.executable,
                "-m",
                "git_author_stats",
                "https://github.com/enorganic/git-author-stats.git",
                "-f",
                "1w",
                "--since",
                (date.today() - timedelta(days=365)).isoformat(),
                "-md",
            ),
        )
        .strip()
        .split("\n")
    )
    assert len(lines) > 2
    # CSV
    lines = (
        check_output(
            (
                sys.executable,
                "-m",
                "git_author_stats",
                "https://github.com/enorganic/git-author-stats.git",
                "-f",
                "1w",
                "--since",
                (date.today() - timedelta(days=365)).isoformat(),
            ),
        )
        .strip()
        .split("\n")
    )
    assert len(lines) > 2


def test_read_write() -> None:
    """
    Test read/write functions
    """
    stats: Iterable[Stats] = read_stats(STATS_CSV_PATH)
    if STATS_TSV_PATH.exists():
        tsv_contents: str
        with open(STATS_TSV_PATH, "rt", errors="ignore") as file:
            tsv_contents = file.read().strip()
        # Explicitly indicate the file format
        tsv_io: StringIO = StringIO()
        write_stats(read_stats(STATS_CSV_PATH), tsv_io, delimiter="\t")
        tsv_io.seek(0)
        test_tsv_contents: str = tsv_io.read().strip()
        assert test_tsv_contents == tsv_contents
        # Infer the format from the file name
        tsv_io = StringIO()
        tsv_io.name = "stats.tsv"
        write_stats(read_stats(STATS_CSV_PATH), tsv_io, delimiter="\t")
        tsv_io.seek(0)
        test_tsv_contents = tsv_io.read().strip()
        assert test_tsv_contents == tsv_contents
    else:
        write_stats(stats, STATS_TSV_PATH)
    if STATS_MD_PATH.exists():
        md_contents: str
        with open(STATS_MD_PATH, "rt", errors="ignore") as file:
            md_contents = file.read().strip()
        # Explicitly indicate the file format
        md_io: StringIO = StringIO()
        write_stats(read_stats(STATS_CSV_PATH), md_io, markdown=True)
        md_io.seek(0)
        test_md_contents: str = md_io.read().strip()
        assert test_md_contents == md_contents
        # Infer the format from the file name
        md_io = StringIO()
        md_io.name = "stats.md"
        write_stats(read_stats(STATS_CSV_PATH), md_io, markdown=True)
        md_io.seek(0)
        test_md_contents = md_io.read().strip()
        assert test_md_contents == md_contents
    else:
        write_stats(
            read_stats(STATS_TSV_PATH),
            STATS_MD_PATH,
        )


if __name__ == "__main__":
    pytest.main(["-s", "-vv", __file__])
