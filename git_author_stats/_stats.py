import csv
import os
import re
import shutil
import unicodedata
from copy import copy
from dataclasses import Field, dataclass, fields
from datetime import date, datetime, timedelta
from enum import Enum
from operator import itemgetter
from pathlib import Path
from subprocess import DEVNULL, PIPE, CalledProcessError, list2cmdline, run
from tempfile import mkdtemp
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Set,
    TextIO,
    Tuple,
    Union,
    cast,
)
from urllib.parse import ParseResult
from urllib.parse import quote as _quote
from urllib.parse import urlparse, urlunparse

cache: Callable[[Callable], Callable]
try:
    from functools import cache  # type: ignore
except ImportError:
    from functools import lru_cache

    cache = lru_cache(maxsize=None)

GIT: str = shutil.which("git") or "git"


def check_output(
    args: Tuple[str, ...],
    cwd: Union[str, Path] = "",
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
            print("$", "cd", cwd, "&&", list2cmdline(args))
        else:
            print("$", list2cmdline(args))
    output: str = run(
        args,
        stdout=PIPE,
        stderr=DEVNULL,
        check=True,
        cwd=cwd or None,
    ).stdout.decode("utf-8", errors="ignore")
    if echo:
        print(output)
    return output


def get_iso_date(datetime_string: str) -> Optional[date]:
    return (
        datetime.fromisoformat(datetime_string.strip().rstrip("Z")).date()
        if datetime_string
        else None
    )


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
    assert url
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
    if password:
        assert url != updated_url
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
    from ._github import iter_organization_repository_clone_urls

    repository_url: str
    for repository_url in iter_organization_repository_clone_urls(
        url, user, password
    ):
        yield repository_url


def iter_clone(
    urls: Union[str, Iterable[str]],
    user: str = "",
    password: str = "",
    since: Optional[date] = None,
) -> Iterable[Tuple[str, str]]:
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
        else:
            path = clone(url, user=user, password=password, since=since)
            if path:
                yield url, path


def clone(
    url: str,
    user: str = "",
    password: str = "",
    since: Optional[date] = None,
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
    os.chmod(temp_directory, 0o777)
    command: Tuple[str, ...] = (
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
            except Exception:
                raise error
            # Cleanup the directory and return an empty string to indicate no
            # relevant commits were found
            shutil.rmtree(temp_directory)
            return ""
        shutil.rmtree(temp_directory)
        raise error
    return temp_directory


def normalize_author(author: str) -> str:
    """
    Normalize an author name.
    """
    return unicodedata.normalize("NFKD", author).strip().capitalize()


def iter_local_repo_author_names(
    path: Union[str, Path] = "",
    email: bool = False,
) -> Iterable[str]:
    # Only look for authors if there is at least one commit
    if int(
        check_output(
            (GIT, "rev-list", "--all", "--count"),
            cwd=path,
        ).strip()
    ):
        line: str
        output: str = check_output(
            (GIT, "--no-pager", "log"),
            cwd=path,
        )
        names: Set[str] = set()
        for line in filter(
            None,
            output.strip().split("\n"),
        ):
            if line.startswith("Author:"):
                name = line[7:].strip()
                if not email:
                    name = name.partition("<")[0].rstrip()
                if name not in names:
                    names.add(name)
                    yield name


def map_authors_names_normalized(names: Iterable[str]) -> Dict[str, str]:
    """
    Return a dictionary of author names, mapped to a normalized author name

    Parameters:

    - path (str): The path to the local repository
    """
    names_normalized: Dict[str, str] = {}
    for name in names:
        names_normalized[name] = normalize_author(name)
    return names_normalized


def is_new_name_better_formatted(old: str, new: str) -> int:
    """
    Is `new` a better formatted variation of the name than `old`?
    """
    if old == new:
        return False
    # Pick the longer name, if there is a difference, defaulting to `old`
    # if they are the same length
    if len(old) < len(new):
        return True
    # Pick the one which has casing variation
    old_is_uncased: bool = old.isupper() or old.islower()
    new_is_uncased: bool = new.isupper() or new.islower()
    if old_is_uncased and not new_is_uncased:
        return True
    if new_is_uncased and not old_is_uncased:
        return False
    return False


def map_authors_regular_expression_aliases(
    names: Iterable[str],
    regular_expression_aliases: Union[
        Mapping[str, str],
        Tuple[Tuple[str, str], ...],
    ] = (),
) -> Dict[str, str]:
    patterns_aliases: MutableMapping[re.Pattern[str], str] = {}
    if not isinstance(regular_expression_aliases, Mapping):
        regular_expression_aliases = dict(regular_expression_aliases)
    key: str
    value: str
    for key, value in regular_expression_aliases.items():
        patterns_aliases[re.compile(key)] = value
    pattern: re.Pattern[str]
    names_aliases: Dict[str, str] = {}
    for name in names:
        for pattern, value in patterns_aliases.items():
            if pattern.match(name):
                names_aliases[name] = value
                # Use the first matched alias for each name
                break
    return names_aliases


def map_authors_aliases(
    names: Iterable[str],
    regular_expression_aliases: Union[
        Mapping[str, str],
        Tuple[Tuple[str, str], ...],
    ] = (),
    email: bool = False,
) -> Dict[str, str]:
    """
    Return a dictionary mapping author names to the best formatted variation
    of the author's name, or to an alias, if the name matches any of the
    regular expressions in `regular_expression_aliases`.

    Parameters:

    - names ([str]): Commit author names
    - regular_expression_aliases ({str: str}|((str, str),)): A mapping of
      regular expressions to aliases
    - email (bool) = False: Include email addresses in automatically
      generated aliases
    """
    names_aliases: Dict[str, str] = map_authors_regular_expression_aliases(
        names,
        regular_expression_aliases,
    )
    names_normalized: Dict[str, str] = map_authors_names_normalized(names)
    # Map a normalized name to the best formatted variation
    normalized_best: Dict[str, str] = {}
    name: str
    name_normalized: str
    for name, name_normalized in names_normalized.items():
        if name_normalized not in normalized_best:
            normalized_best[name_normalized] = name
        else:
            if is_new_name_better_formatted(
                normalized_best[name_normalized], name
            ):
                normalized_best[name_normalized] = name
    # Map all names to their best formatted variation
    names_best: Dict[str, str] = {}
    for name, name_normalized in names_normalized.items():
        best_name: str = normalized_best[name_normalized]
        # If the name has an alias, use the alias
        if name in names_aliases:
            best_name = names_aliases[name]
        elif best_name in names_aliases:
            best_name = names_aliases[best_name]
        # Remove the email address if it's not wanted in our output
        if not email:
            best_name = best_name.partition("<")[0].rstrip()
            name = name.partition("<")[0].rstrip()
        names_best[name] = best_name
    return names_best


class FrequencyUnit(Enum):
    """
    A unit of time.
    """

    WEEK: str = "week"
    MONTH: str = "month"
    DAY: str = "day"
    YEAR: str = "year"


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
    matched: Optional[re.Match] = _FREQUENCY_PATTERN.match(frequency_string)
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
    Inserted and deleted lines of code for an author, optionally in
    a specific repository and/or during a specific time period.
    """

    url: str = ""
    author: str = ""
    since: Optional[date] = None
    before: Optional[date] = None
    insertions: int = 0
    deletions: int = 0
    file: str = ""

    def __init__(
        self,
        url: str = "",
        author: str = "",
        since: Union[date, str, None] = None,
        before: Union[date, str, None] = None,
        insertions: Union[int, str] = 0,
        deletions: Union[int, str] = 0,
        file: str = "",
    ) -> None:
        if isinstance(since, str):
            since = get_iso_date(since)
        if isinstance(before, str):
            before = get_iso_date(before)
        if isinstance(insertions, str):
            insertions = int(insertions)
        if isinstance(deletions, str):
            deletions = int(deletions)
        self.url: str = url
        self.author: str = author
        self.since: date = since
        self.before: date = before
        self.insertions: int = insertions
        self.deletions: int = deletions
        self.file: str = file


_STATS_PATTERN: re.Pattern = re.compile(
    r"[^\d]*?([\d\-]+)\s+([\d\-]+)\s+([^\n]+)(?:\n|$)",
    flags=re.IGNORECASE,
)


def get_first_author_date(path: Union[str, Path] = "") -> date:
    output: str = check_output(
        (GIT, "log", "--reverse", "--date=iso8601-strict"),
        cwd=path,
    ).strip()
    line: str
    for line in output.split("\n"):
        if line.startswith("Date:"):
            return cast(date, get_iso_date(line[5:]))
    raise ValueError(output)


def iter_local_repo_stats(
    path: str,
    author: str,
    since: Optional[date] = None,
    before: Optional[date] = None,
) -> Iterable[Stats]:
    line: str
    command: Tuple[str, ...] = (
        GIT,
        "--no-pager",
        "log",
        "--author",
        author,
        "--format=tformat:",
        "--numstat",
    )
    if since is not None:
        command += ("--since", since.isoformat())
    if before is not None:
        command += ("--before", before.isoformat())
    file_stats: Dict[str, Stats] = {}
    for line in filter(
        None,
        map(str.strip, check_output(command, cwd=path).strip().split("\n")),
    ):
        matched: Optional[re.Match] = _STATS_PATTERN.match(line)
        if not matched:
            raise ValueError(line)
        stats: Stats = Stats(
            author=author,
            since=since,
            before=before,
            insertions=int(matched.group(1).rstrip("-") or 0),
            deletions=int(matched.group(2).rstrip("-") or 0),
            file=matched.group(3),
        )
        if stats.file in file_stats:
            file_stats[stats.file].insertions += stats.insertions
            file_stats[stats.file].deletions += stats.deletions
        else:
            file_stats[stats.file] = stats
    yield from file_stats.values()


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


def iter_date_ranges(
    since: date,
    after: Optional[date] = None,
    before: Optional[date] = None,
    until: Optional[date] = None,
    frequency: Union[Frequency, str, None] = None,
) -> Iterable[Tuple[Optional[date], Optional[date]]]:
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
    if after is not None:
        if since:
            since = max(since, after + timedelta(days=1))
        else:
            since = after + timedelta(days=1)
    if until is not None:
        if before:
            before = min(before, until + timedelta(days=1))
        else:
            before = until + timedelta(days=1)
    if frequency is None:
        yield since, before
        return
    if isinstance(frequency, str):
        frequency = parse_frequency_string(frequency)
    if not before:
        before = date.today() + timedelta(days=1)
    assert since < before
    increment_frequency: Frequency
    period_since: date = since
    period_before: date = increment_date_by_frequency(since, frequency)
    period: int = 1
    new_period_before: date
    while period_since < before:
        yield period_since, (
            min(period_before, before) if before else period_before
        )
        increment_frequency = copy(frequency)
        period += 1
        increment_frequency.quantity *= period
        new_period_before = increment_date_by_frequency(
            since, increment_frequency
        )
        period_since = period_before
        period_before = new_period_before


def iter_stats(  # noqa: C901
    urls: Union[str, Iterable[str]],
    user: str = "",
    password: str = "",
    since: Optional[date] = None,
    after: Optional[date] = None,
    before: Optional[date] = None,
    until: Optional[date] = None,
    frequency: Union[str, Frequency, None] = None,
    regular_expression_aliases: Union[
        Mapping[str, str], Tuple[Tuple[str, str], ...]
    ] = (),
    email: bool = False,
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
    - regular_expression_aliases (((str, str),)) = ():
    """
    if isinstance(frequency, str):
        frequency = parse_frequency_string(frequency)
    urls_paths: Tuple[Tuple[str, str], ...] = tuple(
        iter_clone(urls, user, password, since=since)
    )
    url: str
    path: str
    # Author names by path
    paths_authors: Dict[str, Tuple[str, ...]] = {}
    # All author names
    author_names: Tuple[str, ...]
    all_author_names_emails: Set[str] = set()
    first_author_date: Optional[date] = None
    for path in map(itemgetter(1), urls_paths):
        if since is None:
            if first_author_date is None:
                first_author_date = get_first_author_date(path)
            else:
                first_author_date = min(
                    get_first_author_date(path), first_author_date
                )
        author_names = tuple(iter_local_repo_author_names(path, email))
        paths_authors[path] = author_names
        # The author names used for mapping aliases needs to include email
        # addresses
        all_author_names_emails |= (
            set(author_names)
            if email
            else set(iter_local_repo_author_names(path, email=True))
        )
    if since is None:
        since = first_author_date
    if before is None:
        before = date.today() + timedelta(days=1)
    assert since and before and since < before
    # Get a mapping of author names to the best formatted variation of the
    # author's name
    authors_aliases: Dict[str, str] = map_authors_aliases(
        all_author_names_emails,
        regular_expression_aliases,
        email=email,
    )
    # Yield stats for each author, for each repository, for each time period
    for url, path in urls_paths:
        author_names = paths_authors[path]
        author_name: str
        for author_name in author_names:
            period_since: Optional[date]
            period_before: Optional[date]
            for period_since, period_before in iter_date_ranges(
                since=since,
                after=after,
                before=before,
                until=until,
                frequency=frequency,
            ):
                stats: Stats
                for stats in iter_local_repo_stats(
                    path,
                    author=author_name,
                    since=period_since,
                    before=period_before,
                ):
                    stats.url = url
                    stats.author = authors_aliases[stats.author]
                    yield stats


def get_string_value(value: Union[str, date, float, int, None]) -> str:
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def write_markdown_table(
    file: Union[str, Path, TextIO],
    rows: List[Tuple[str, ...]],
    no_header: bool = False,
) -> None:
    """
    Write a Markdown table representation of a list of equal-length tuples.

    Parameters:

    - file (str|pathlib.Path|typing.TextIO): A file path or file-like object
    - rows (List[Tuple[str, ...]): The rows in the table.
    """
    if isinstance(file, (str, Path)):
        file = open(file, "wt")
    if rows and no_header:
        rows = rows[1:]
    if not rows:
        return
    index: int
    row: Tuple[str, ...]
    indices: Tuple[int, ...] = tuple(range(len(rows[0])))
    column_widths: Tuple[int, ...] = tuple(
        map(lambda index: max(map(lambda row: len(row[index]), rows)), indices)
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


def _get_file_path(file: Union[str, Path, TextIO]) -> Optional[Path]:
    if isinstance(file, (str, Path)):
        if isinstance(file, str):
            return Path(file)
        else:
            return file
    else:
        if hasattr(file, "name"):
            return Path(file.name)
    return None


def _get_path_delimiter(path: Path) -> str:
    extension: str = path.suffix.lower().lstrip(".").lower()
    return "" if extension == "md" else "\t" if extension == "tsv" else ","


@cache
def _get_stats_field_names() -> Tuple[str, ...]:
    field: Field
    return tuple(map(lambda field: field.name, fields(Stats)))


def write_stats(
    stats: Iterable[Stats],
    file: Union[str, Path, TextIO],
    no_header: bool = False,
    delimiter: str = "",
    markdown: Optional[bool] = None,
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
    path: Optional[Path] = _get_file_path(file)
    if (not (markdown or delimiter)) and (path is not None):
        delimiter = _get_path_delimiter(path)
    if markdown is None:
        markdown = bool(
            (not delimiter)
            and ((path is None) or path.suffix.lower().lstrip(".") == "md")
        )
    # Open a file for writing, if necessary
    file_io: TextIO
    if isinstance(file, (str, Path)):
        file_io = open(file, "wt")
    else:
        file_io = file
    # Get the header
    field_names: Tuple[str, ...] = _get_stats_field_names()
    # The `rows` list will only be needed for markdown output
    rows: List[Tuple[str, ...]]
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
        row: Tuple[str, ...] = tuple(
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
    file: Union[str, Path, TextIO],
    delimiter: str = "",
) -> Iterable[Stats]:
    if not delimiter:
        path: Optional[Path] = _get_file_path(file)
        if path is not None:
            delimiter = _get_path_delimiter(path)
    if isinstance(file, (str, Path)):
        file = open(file, "rt", errors="ignore")
    if delimiter:
        delimiter = delimiter.replace("\\t", "\t")
    field_names: List[str] = list(_get_stats_field_names())
    row: List[str]
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
