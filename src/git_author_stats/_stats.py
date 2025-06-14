from __future__ import annotations

import csv
import os
import re
import shutil
from copy import copy
from dataclasses import Field, dataclass, fields
from datetime import date, datetime, timedelta, timezone
from enum import Enum
from io import BytesIO
from operator import itemgetter
from pathlib import Path
from subprocess import (
    DEVNULL,
    PIPE,
    CalledProcessError,
    Popen,
    list2cmdline,
    run,
)
from tempfile import mkdtemp
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    TextIO,
    cast,
)
from urllib.parse import ParseResult, urlparse, urlunparse
from urllib.parse import quote as _quote

if TYPE_CHECKING:
    from collections.abc import Iterable

cache: Callable[[Callable], Callable]
try:
    from functools import cache  # type: ignore
except ImportError:
    from functools import lru_cache

    cache = lru_cache(maxsize=None)

GIT: str = shutil.which("git") or "git"


def check_output(
    args: tuple[str, ...],
    cwd: str | Path = "",
    *,
    echo: bool = False,
) -> str:
    """
    This function mimics `subprocess.check_output`, but redirects stderr
    to DEVNULL, and ignores unicode decoding errors.

    Parameters:

    - command (Tuple[str, ...]): The command to run
    """
    if echo:
        if cwd:
            print("$", "cd", cwd, "&&", list2cmdline(args))  # noqa: T201
        else:
            print("$", list2cmdline(args))  # noqa: T201
    output: str = run(
        args,
        stdout=PIPE,
        stderr=DEVNULL,
        check=True,
        cwd=cwd or None,
    ).stdout.decode("utf-8", errors="ignore")
    if echo:
        print(output)  # noqa: T201
    return output


def iter_output(
    args: tuple[str, ...],
    cwd: str | Path = "",
    *,
    echo: bool = False,
) -> Iterable[str]:
    """
    This function runs a command in a subprocess, redirecting stderr
    to DEVNULL, ignoring unicode decoding errors, and yields lines returned
    from the subprocess as they are received.

    Parameters:

    - args (Tuple[str, ...]): The command to run
    - cwd (str|pathlib.Path) = "": The working directory in which to run the
      command
    """
    if echo:
        if cwd:
            print("$", "cd", cwd, "&&", list2cmdline(args))  # noqa: T201
        else:
            print("$", list2cmdline(args))  # noqa: T201
    process: Popen = Popen(
        args,
        stdout=PIPE,
        stderr=DEVNULL,
        cwd=cwd or None,
    )
    return_code: int | None = None
    try:
        bline: bytes
        for bline in iter(cast(BytesIO, process.stdout).readline, b""):
            line: str = bline.decode("utf-8", errors="ignore").rstrip("\n")
            if echo:
                print(line)  # noqa: T201
            yield line
        return_code = process.wait()
    except Exception:
        process.kill()
        raise
    if return_code:
        raise CalledProcessError(return_code, args)


def get_iso_datetime(datetime_string: str) -> datetime | None:
    """
    Get a date and time from an ISO 8601 formatted string, or `None` if
    the string is empty.
    """
    if not datetime_string:
        return None
    date_time: datetime = datetime.fromisoformat(
        datetime_string.strip().rstrip("Z")
    )
    # Convert to UTC if the date/time has a timezone
    if date_time.tzinfo is not None:
        date_time = date_time.astimezone(timezone.utc).replace(tzinfo=None)
    return date_time


def get_iso_date(datetime_string: str) -> date | None:
    """
    Get a date from an ISO 8601 formatted string, or `None` if
    the string is empty.
    """
    if not datetime_string:
        return None
    iso_datetime: datetime = cast(datetime, get_iso_datetime(datetime_string))
    return iso_datetime.date()


def update_url_user_password(
    url: str,
    user: str = "",
    password: str = "",
    quote: Callable[[str], str] = _quote,
) -> str:
    """
    Update a URL's user and password and return the result.

    Parameters:

    - url (str)
    - user (str) = ""
    - password (str) = "": (optional)
    - quote = urllib.parse.quote: A function to use for escaping
      invalid character (defaults to `urllib.parse.quote`)
    """
    if not url:
        raise ValueError(url)
    if not (user or password):
        return url
    parse_result: ParseResult = urlparse(url)
    host: str
    user_password: str
    user_password, host = parse_result.netloc.rpartition("@")[::2]
    if user and password:
        user_password = f"{quote(user)}:{quote(password)}"
    elif user:
        user_password = quote(user)
    elif password:
        user_password = user_password.partition(":")[0]
        if user_password:
            # The URL already had a user name in it, so we will use that.
            # Since we know that a user name was not provided, and that we'd
            # have returned the original URL already if neither user name nor
            # password had been provided, we know that we have a `password` to
            # append, so we will drop any password which might have been
            # parsed from the URL.
            user_password = f"{user_password}:{quote(password)}"
        else:
            # The password is a token
            user_password = quote(password)
    updated_url: str = urlunparse(
        (
            parse_result.scheme,
            f"{user_password}@{host}",
            parse_result.path,
            parse_result.params,
            parse_result.query,
            parse_result.fragment,
        )
    )
    if password and url == updated_url:
        raise ValueError((url, user, password))
    return updated_url


def is_github_organization(
    url: str,
) -> bool:
    """
    Is this URL for a Github organization (as opposed to a repository)?
    """
    if "://" not in url:
        url = f"https://{url}"
    parse_result: ParseResult = urlparse(url)
    host: str = parse_result.netloc.rpartition("@")[-1].lower()
    # If the host is not github.com, then this is a not a URL for a Github
    # organization
    if host != "github.com" and not host.endswith(".github.com"):
        return False
    # Github orgs are top-level paths
    return "/" not in parse_result.path.strip("/")


def iter_github_organization_repository_urls(
    url: str, user: str = "", password: str = ""
) -> Iterable[str]:
    """
    Yield the URLs of all repositories in a Github organization which
    are accessible to the specified user
    """
    from git_author_stats._github import (
        iter_organization_repository_clone_urls,
    )

    yield from iter_organization_repository_clone_urls(url, user, password)


def iter_clone(
    urls: str | Iterable[str],
    user: str = "",
    password: str = "",
    since: date | None = None,
) -> Iterable[tuple[str, str]]:
    """
    Clone one or more Git repositories to temp directories and yield the
    paths of all temp directories created (one for each repository).

    Parameters:

    - urls (str|[str]): One or more git URLs, as you would pass to `git clone`,
      or the URL of a Github organization
    - user (str) = "": A username with which to authenticate.
      Note: If neither user name nor password are provided, the default system
      configuration will be used.
    - password (str) = "": A password/token with which to authenticate.
    - since (date|None) = None: If provided, the clone will be shallow, only
      including commits on or after this date
    """
    if isinstance(urls, str):
        urls = (urls,)
    url: str
    path: str
    for url in urls:
        if is_github_organization(url):
            # Clone all repositories in the organization
            repository_url: str
            for repository_url in iter_github_organization_repository_urls(
                url, user, password
            ):
                path = clone(
                    repository_url, user=user, password=password, since=since
                )
                if path:
                    yield repository_url, path
        elif os.path.isdir(url):
            # If this is a local directory, there is no need to clone it
            yield url, url
        else:
            path = clone(url, user=user, password=password, since=since)
            if path:
                yield url, path


def clone(
    url: str,
    user: str = "",
    password: str = "",
    since: date | None = None,
) -> str:
    """
    Clone a Git repository to a temp directory and return the path of the
    temp directory.

    Parameters:

    - url (str): A git URL, as you would pass to `git clone`
    - user (str) = ""
    - password (str) = ""
    - since (date) = None: If provided, the clone will be shallow, only
      including commits on or after this date
    """
    url = update_url_user_password(url, user, password)
    # Clone into a temp directory
    temp_directory: str = mkdtemp()
    os.chmod(temp_directory, 0o777)  # noqa: S103
    command: tuple[str, ...] = (
        GIT,
        "clone",
        "-q",
        "--filter=blob:none",
        "--bare",
    )
    if since is not None:
        command += (f"--shallow-since={since.isoformat()}",)
    command += (url, temp_directory)
    try:
        check_output(command)
    except CalledProcessError as error:
        if since is not None:
            # Test to see if the error was due to the date
            try:
                shutil.rmtree(
                    clone(url, user=user, password=password),
                    # We only care about errors from the `clone` function call,
                    # `rmtree` is just a cleanup operation
                    ignore_errors=True,
                )
            except Exception:  # noqa: BLE001
                raise error from None
            # Cleanup the directory and return an empty string to indicate no
            # relevant commits were found
            shutil.rmtree(temp_directory)
            return ""
        shutil.rmtree(temp_directory)
        raise
    return temp_directory


class FrequencyUnit(Enum):
    """
    A unit of time.
    """

    WEEK = "week"
    MONTH = "month"
    DAY = "day"
    YEAR = "year"


@dataclass
class Frequency:
    """
    A frequency of time.
    """

    quantity: int
    unit: FrequencyUnit


_FREQUENCY_PATTERN: re.Pattern = re.compile(
    r"[^\d]*?(\d+)?\s*([a-zA-Z]).*",
    flags=re.IGNORECASE,
)


def parse_frequency_string(frequency_string: str) -> Frequency:
    """
    Parse a frequency string. Frequency should be a number, followed by a unit
    or abbreviation. For example, all of the following are acceptable values:
    "1 week", "2 months", "3 days", "1m", "2w", or "3D".

    Examples:

    >>> parse_frequency_string("1 week")
    Frequency(quantity=1, unit=<FrequencyUnit.WEEK: 'week'>)
    >>> parse_frequency_string("1w")
    Frequency(quantity=1, unit=<FrequencyUnit.WEEK: 'week'>)
    >>> parse_frequency_string("w")
    Frequency(quantity=1, unit=<FrequencyUnit.WEEK: 'week'>)
    >>> parse_frequency_string("weeks")
    Frequency(quantity=1, unit=<FrequencyUnit.WEEK: 'week'>)
    """
    matched: re.Match | None = _FREQUENCY_PATTERN.match(frequency_string)
    if not matched:
        raise ValueError(frequency_string)
    unit: str = matched.group(2).lower()
    member: FrequencyUnit
    for member in FrequencyUnit.__members__.values():
        if cast(str, member.value).lower().startswith(unit):
            return Frequency(
                # Default to 1 if no quantity is provided
                int(matched.group(1) or 1),
                member,
            )
    raise ValueError(frequency_string)


@dataclass
class Stats:
    """
    This object represents metrics obtained from the output of
    `git log --numstat`. Each record is unique when grouped by
    url + commit + author_name + file. The fields `since` and `before`
    are provided as a convenience for easy aggregation of stats, but do not
    provide any additional information about the commit or file.

    Properties:

    - url (str): The URL of the repository
    - since (date|None): The start date for a pre-defined time period by which
      these metrics will be analyzed
    - before (date|None): The end date (non-inclusive) for a pre-defined time
      period by which these metrics will be analyzed
    - author_date (datetime|None): The date and time of the author's commit
    - author_name (str): The name of the author
    - commit (str): The abbreviated commit hash
    - file (str): The file path
    - insertions (int): The number of lines inserted in this commit
    - deletions (int): The number of lines deleted in this commit
    """

    url: str = ""
    since: date | None = None
    before: date | None = None
    author_date: datetime | None = None
    author_name: str = ""
    commit: str = ""
    file: str = ""
    insertions: int = 0
    deletions: int = 0

    def __init__(
        self,
        url: str = "",
        since: date | str | None = None,
        before: date | str | None = None,
        author_date: datetime | str | None = None,
        author_name: str = "",
        commit: str = "",
        file: str = "",
        insertions: int | str = 0,
        deletions: int | str = 0,
    ) -> None:
        if isinstance(since, str):
            since = get_iso_date(since)
        if isinstance(before, str):
            before = get_iso_date(before)
        if isinstance(author_date, str):
            author_date = get_iso_datetime(author_date)
        if isinstance(insertions, str):
            insertions = int(insertions)
        if isinstance(deletions, str):
            deletions = int(deletions)
        self.url: str = url
        self.since: date = since
        self.before: date = before
        self.author_date: datetime = author_date
        self.author_name: str = author_name
        self.commit: str = commit
        self.file: str = file
        self.insertions: int = insertions
        self.deletions: int = deletions


_STATS_PATTERN: re.Pattern = re.compile(
    r"[^\d]*?([\d\-]+)\s+([\d\-]+)\s+([^\n]+)(?:\n|$)",
    flags=re.IGNORECASE,
)


def get_first_author_date(path: str | Path = "") -> date:
    output: str = check_output(
        (GIT, "log", "--reverse", "--date=iso8601-strict"),
        cwd=path,
    ).strip()
    line: str
    for line in output.split("\n"):
        if line.startswith("Date:"):
            return cast(date, get_iso_date(line[5:]))
    raise ValueError(output)


def _get_datetime_str(now: datetime | date) -> str:
    now_str: str = now.isoformat()
    if isinstance(now, datetime):
        now_str = now.isoformat()
        if now.tzinfo is None:
            now_str = f"{now_str}Z"
    else:
        now_str = f"{now.isoformat()}T00:00Z"
    return now_str


def iter_local_repo_stats(
    path: str,
    author: str = "",
    since: date | datetime | None = None,
    before: date | datetime | None = None,
    *,
    no_mailmap: bool = True,
) -> Iterable[Stats]:
    """
    Yield stats for a local repository, optionally for a specific author
    and/or date range
    """
    line: str
    command: tuple[str, ...] = (
        GIT,
        "--no-pager",
        "log",
        "--numstat",
        "--date=iso-strict",
        ("--format=tformat:" "commit:%h%nauthor_name:%an%nauthor_date:%ad"),
    )
    if no_mailmap:
        command += ("--no-mailmap",)
    else:
        command += ("--mailmap",)
    if author:
        command += ("--author", author)
    if since is not None:
        command += ("--since", _get_datetime_str(since))
    if before is not None:
        command += ("--before", _get_datetime_str(before))
    commit: str = ""
    author_name: str = ""
    author_date: str = ""
    for line in (
        filter(
            None,
            map(str.strip, iter_output(command, cwd=path)),
        )
        if int(  # Only look for stats if there is at least one commit
            check_output(
                (GIT, "rev-list", "--all", "--count"),
                cwd=path,
            ).strip()
        )
        else ()
    ):
        if line.startswith("commit:"):
            commit = line[7:]
            continue
        if line.startswith("author_name:"):
            author_name = line[12:]
            continue
        if line.startswith("author_date:"):
            author_date = line[12:]
            continue
        matched: re.Match | None = _STATS_PATTERN.match(line)
        if not matched:
            raise ValueError(line)
        yield Stats(
            since=since,
            before=before,
            author_date=author_date,
            author_name=author_name,
            commit=commit,
            file=matched.group(3),
            insertions=int(matched.group(1).rstrip("-") or 0),
            deletions=int(matched.group(2).rstrip("-") or 0),
        )


def increment_date_by_frequency(today: date, frequency: Frequency) -> date:
    """
    Increment a date by the specified frequency
    """
    if frequency.unit == FrequencyUnit.WEEK:
        return today + timedelta(weeks=frequency.quantity)
    if frequency.unit == FrequencyUnit.DAY:
        return today + timedelta(days=frequency.quantity)
    if frequency.unit == FrequencyUnit.YEAR:
        return date(today.year + frequency.quantity, today.month, today.day)
    if frequency.unit == FrequencyUnit.MONTH:
        month: int = today.month + frequency.quantity
        year: int = today.year
        if month > 12:
            year += int(month / 12)
            month = (month % 12) or 12
        # If the incremented month's day is invalid for that month, decrement
        # the day until we find a valid day
        day: int
        for day in range(today.day, 0, -1):
            try:
                return date(year, month, day)
            except ValueError:
                pass
    raise ValueError((today, frequency))


def get_date_range(
    since: date | None = None,
    after: date | None = None,
    before: date | None = None,
    until: date | None = None,
) -> tuple[date, date]:
    """
    Get a since/before date range
    """
    if after is not None:
        if since is not None:
            since = max(since, after + timedelta(days=1))
        else:
            since = after + timedelta(days=1)
    if until is not None:
        if before is not None:
            before = min(before, until + timedelta(days=1))
        else:
            before = until + timedelta(days=1)
    if since is None:
        raise ValueError((since, after, before, until))
    if not before:
        before = datetime.now(tz=timezone.utc).date() + timedelta(days=1)
    return since, before


def iter_date_ranges(
    since: date | None = None,
    after: date | None = None,
    before: date | None = None,
    until: date | None = None,
    frequency: Frequency | str | None = None,
) -> Iterable[tuple[date, date]]:
    """
    Iterate over all date ranges for the specified time period

    Parameters:

    - since (date|None) = None: If provided, only yield stats since this date
      (inclusive)
    - after (date|None) = None: If provided, only yield stats after this date
      (non-inclusive)
    - before (date|None) = None: If provided, only yield stats before this date
      (non-inclusive)
    - until (date|None) = None: If provided, only yield stats until this date
      (inclusive)
    - frequency (str|Frequency|None) = None: A frequency of time. If not
      provided, only one date range will be yielded.
    """
    since, before = get_date_range(since, after, before, until)
    if frequency is None:
        yield since, before
        return
    if isinstance(frequency, str):
        frequency = parse_frequency_string(frequency)
    increment_frequency: Frequency
    period_since: date = since
    period_before: date = increment_date_by_frequency(since, frequency)
    period: int = 1
    new_period_before: date
    while period_since < before:
        yield (
            period_since,
            (min(period_before, before) if before else period_before),
        )
        increment_frequency = copy(frequency)
        period += 1
        increment_frequency.quantity *= period
        new_period_before = increment_date_by_frequency(
            since, increment_frequency
        )
        period_since = period_before
        period_before = new_period_before


def _iter_date_range_map(
    frequency: str | Frequency,
    since: date | None = None,
    after: date | None = None,
    before: date | None = None,
    until: date | None = None,
) -> Iterable[tuple[date, tuple[date, date]]]:
    period_since: date
    period_before: date
    for period_since, period_before in iter_date_ranges(
        since=since,
        after=after,
        before=before,
        until=until,
        frequency=frequency,
    ):
        day: date = period_since
        while day < period_before:
            yield day, (period_since, period_before)
            day += timedelta(days=1)


def get_date_range_map(
    frequency: str | Frequency,
    since: date | None = None,
    after: date | None = None,
    before: date | None = None,
    until: date | None = None,
) -> dict[date, tuple[date, date]]:
    """
    Get dictionary mapping dates to date ranges
    """
    return dict(_iter_date_range_map(frequency, since, after, before, until))


def iter_stats(  # noqa: C901
    urls: str | Iterable[str],
    user: str = "",
    password: str = "",
    since: date | None = None,
    after: date | None = None,
    before: date | None = None,
    until: date | None = None,
    frequency: str | Frequency | None = None,
    *,
    no_mailmap: bool = False,
) -> Iterable[Stats]:
    """
    Yield stats for all specified repositories, by author, for the specified
    time period and frequency (if provided).

    Parameters:

    - urls (str|[str]): One or more git URLs, as you would pass to `git clone`,
      or the URL of a Github organization
    - user (str) = "": A username with which to authenticate.
      Note: If neither user name nor password are provided, the default system
      configuration will be used.
    - password (str) = "": A password/token with which to authenticate.
    - since (date|None) = None: If provided, only yield stats after this date
    - before (date|None) = None: If provided, only yield stats before this date
    - frequency (str|Frequency|None) = None: If provided, yield stats
      broken down by the specified frequency. For example, if `frequency` is
      "1 week", stats will be yielded for each week in the specified time,
      starting with `since` and ending with `before` (if provided).
    - no_mailmap (bool) = False: If `True`, do not use the mailmap file
    """
    if isinstance(frequency, str):
        frequency = parse_frequency_string(frequency)
    urls_paths: Iterable[tuple[str, str]] = iter_clone(
        urls, user, password, since=since
    )
    url: str
    path: str
    if since is None:
        urls_paths = tuple(urls_paths)
        for path in map(itemgetter(1), urls_paths):
            if since is None:
                since = get_first_author_date(path)
            else:
                since = min(get_first_author_date(path), since)
    if since is None:
        raise ValueError((since, after, before, until))
    if before is None:
        before = datetime.now(tz=timezone.utc).date() + timedelta(days=1)
    since, before = get_date_range(since, after, before, until)
    date_range_map: dict[date, tuple[date, date]] = {}
    if frequency is not None:
        date_range_map = get_date_range_map(
            frequency, since=since, before=before
        )
    # Yield stats for each author, for each repository, for each time period
    for url, path in urls_paths:
        stats: Stats
        for stats in iter_local_repo_stats(
            path,
            since=since,
            before=before,
            no_mailmap=no_mailmap,
        ):
            stats.url = url
            if (frequency is not None) and (stats.author_date is not None):
                stats.since, stats.before = date_range_map.get(
                    stats.author_date.date(), (None, None)
                )
            yield stats


def get_string_value(value: str | date | float | None) -> str:
    if isinstance(value, date):
        return value.isoformat()
    if value is None:
        return ""
    return str(value)


def write_markdown_table(
    file: str | Path | TextIO,
    rows: list[tuple[str, ...]],
    *,
    no_header: bool = False,
) -> None:
    """
    Write a Markdown table representation of a list of equal-length tuples.

    Parameters:

    - file (str|pathlib.Path|typing.TextIO): A file path or file-like object
    - rows (List[Tuple[str, ...]): The rows in the table.
    """
    if isinstance(file, (str, Path)):
        file = open(file, "w")  # noqa: SIM115
    if rows and no_header:
        rows = rows[1:]
    if not rows:
        return
    index: int
    row: tuple[str, ...]
    indices: tuple[int, ...] = tuple(range(len(rows[0])))
    column_widths: tuple[int, ...] = tuple(
        max(len(row[index]) for row in rows) for index in indices
    )
    empty_value: str = " " * max(column_widths)
    is_header: bool = bool(not no_header)
    for row in rows:
        value: str
        file.write(
            "| {} |\n".format(
                " | ".join(
                    f"{value}{empty_value}"[: column_widths[index]]
                    for index, value in zip(indices, row)
                )
            )
        )
        if is_header:
            # Print the header separator
            file.write(
                "| {} |\n".format(
                    " | ".join("-" * column_widths[index] for index in indices)
                )
            )
        is_header = False


def _get_file_path(file: str | Path | TextIO) -> Path | None:
    if isinstance(file, (str, Path)):
        if isinstance(file, str):
            return Path(file)
        return file
    if hasattr(file, "name"):
        return Path(file.name)
    return None


def _get_path_delimiter(path: Path) -> str:
    extension: str = path.suffix.lower().lstrip(".").lower()
    return "" if extension == "md" else "\t" if extension == "tsv" else ","


@cache
def _get_stats_field_names() -> tuple[str, ...]:
    field: Field
    return tuple(field.name for field in fields(Stats))


def write_stats(
    stats: Iterable[Stats],
    file: str | Path | TextIO,
    *,
    no_header: bool = False,
    delimiter: str = "",
    markdown: bool | None = None,
) -> None:
    """
    Write stats for all specified repositories, by author, for the specified
    time period and frequency (if provided), to a CSV file.

    Parameters:

    - stats (typing.Iterable[git_author_stats.Stats]): The stats to write
    - file (str|pathlib.Path|typing.TextIO): A file path or file-like object
    - delimiter (str) = "": The delimiter to use for CSV/TSV output.
      If not provided, the delimiter will be inferred based on the file
      extension if possible, otherwise it will default to ",".
    - markdown (bool|None) = None: If `True`, a markdown table
      will be written. If `False`, a CSV/TSV file will be written.
      If `None`, the output format will be inferred based on the file's
      extension.
    - no_header (bool) = False: Do not include a header in the output
    """
    # Determine the output format
    path: Path | None = _get_file_path(file)
    if (not (markdown or delimiter)) and (path is not None):
        delimiter = _get_path_delimiter(path)
    if markdown is None:
        markdown = bool(
            (not delimiter)
            and ((path is None) or path.suffix.lower().lstrip(".") == "md")
        )
    # Open a file for writing, if necessary
    file_io: TextIO
    file_io = (
        open(file, "w")  # noqa: SIM115
        if isinstance(file, (str, Path))
        else file
    )
    # Get the header
    field_names: tuple[str, ...] = _get_stats_field_names()
    # The `rows` list will only be needed for markdown output
    rows: list[tuple[str, ...]]
    # The CSV writer will only be needed for CSV/TSV output
    csv_writer: Any
    if markdown:
        rows = []
        rows.append(field_names)
    else:
        csv_writer = csv.writer(
            file_io,
            delimiter=(delimiter.replace("\\t", "\t") if delimiter else ","),
            lineterminator="\n",
        )
        if not no_header:
            csv_writer.writerow(field_names)
    stat: Stats
    for stat in stats:
        row: tuple[str, ...] = tuple(
            map(
                get_string_value,
                map(stat.__getattribute__, field_names),
            )
        )
        if markdown:
            rows.append(row)
        else:
            csv_writer.writerow(row)
    if markdown and rows:
        write_markdown_table(file_io, rows, no_header=no_header)


def read_stats(
    file: str | Path | TextIO,
    delimiter: str = "",
) -> Iterable[Stats]:
    if not delimiter:
        path: Path | None = _get_file_path(file)
        if path is not None:
            delimiter = _get_path_delimiter(path)
    if isinstance(file, (str, Path)):
        file = open(file, errors="ignore")  # noqa: SIM115
    if delimiter:
        delimiter = delimiter.replace("\\t", "\t")
    field_names: list[str] = list(_get_stats_field_names())
    row: list[str]
    check_header: bool = True
    for row in csv.reader(
        file,
        delimiter=delimiter or ",",
        lineterminator="\n",
    ):
        if not (check_header and row == field_names):
            yield Stats(*row)
        # Stop checking to see if the row is the header after the first row
        check_header = False
