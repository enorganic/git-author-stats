import os
from datetime import date, timedelta
from typing import Optional

import pandas  # type: ignore
import pytest
from dotenv import load_dotenv

from git_author_stats._stats import (
    Frequency,
    FrequencyUnit,
    Stats,
    get_first_author_date,
    increment_date_by_frequency,
    iter_date_ranges,
    iter_stats,
    parse_frequency_string,
)

load_dotenv()


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


def test_iter_organization_stats() -> None:
    """
    Test obtaining stats for a Github organization
    """
    stats: Stats
    for stats in iter_stats(
        urls="https://github.com/enorganic",
        frequency=Frequency(2, FrequencyUnit.WEEK),
        since=date.today() - timedelta(days=30),
        password=os.environ.get(
            "GH_TOKEN", os.environ.get("GITHUB_TOKEN", "")
        ),
    ):
        print(stats)


def test_iter_repo_stats() -> None:
    """
    Test creating a pandas data frame from the stats of a single repository.
    """
    assert pandas.DataFrame(
        iter_stats(
            urls="https://github.com/enorganic/git-author-stats.git",
            frequency=Frequency(2, FrequencyUnit.WEEK),
            since=date.today() - timedelta(days=365),
            user="davebelais",
        )
    ).columns.tolist() == [
        "url",
        "author",
        "since",
        "before",
        "insertions",
        "deletions",
        "file",
    ]


def test_get_first_author_date() -> None:
    """
    Test getting the first author date using this repository.
    """
    assert get_first_author_date() == date(2024, 4, 30)


if __name__ == "__main__":
    pytest.main(["-s", "-vv", __file__])
