# git-author-stats

[![test](https://github.com/enorganic/git-author-stats/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/enorganic/git-author-stats/actions/workflows/test.yml)
[![distribute](https://github.com/enorganic/git-author-stats/actions/workflows/distribute.yml/badge.svg?branch=main)](https://github.com/enorganic/git-author-stats/actions/workflows/distribute.yml)

This package provides a CLI and library for extracting author "stats"
(insertions and deletions) for a Git repository or Github organization.

Under the hood, these metrics are obtained by:

1. Cloning truncated versions of all specified repositories (or all
   repositories in a specified Github organizations) into temp directories
2. Calculating a series of date ranges based on the temporal limits and
   frequency you've specified
3. Using `git log --numstat` to get a count of the insertions and deletions
   made by each author during each date range

Please note that this package does not provide functionality for aggregation
or analysis of the metrics extracted, instead the output is provided
in a format suitable for use with tools such as [polars](https://pola.rs/),
[pandas](https://pandas.pydata.org/), and
[pyspark](https://spark.apache.org/docs/latest/api/python).

All stats obtained from this package will be unique when grouped by
url + commit + author_name + file, and include the following fields:

- url (str): The URL of the repository (provided because stats for multiple
  repositories can be obtained with one function call or command)
- since (date|None): The start date for a pre-defined time period
  as determined by frequency and time range parameters provided by the user
- before (date|None): The (non-inclusive) end date for a pre-defined time
  period as determined by frequency and time range parameters provided by the
  user
- author_date (datetime.datetime|None): The date and time of the author's
  commit
- author_name (str): The name of the author
- commit (str): The abbreviated commit hash
- file (str): The relative path of the modified file
- insertions (int): The number of lines inserted in this commit
  (please note that this is always 0 for binary files)
- deletions (int): The number of lines deleted in this commit
  (please note that this is always 0 for binary files)

Please note that:

- The fields `since` and `before` are provided as a convenience for easy
  aggregation of stats, based on parameters provided by the user,
  but do not provide any additional information about the commit or file
- All dates and times are expressed in coordinated universal time (UTC),
  as timezone-unaware `datetime.datetime` or `datetime.date` objects in
  python, and output in ISO 8601 format when written to CSV/TSV files and/or
  console output

## Installation

You can install `git-author-stats` with pip:

```shell
pip3 install git-author-stats
```

Please note that you will need to
specify the extra "github" in your `pip install` command if you want to extract
stats from all repositories owned by a _Github organization_ without needing
to provide each repository URL explicitly:

```shell
pip3 install 'git-author-stats[github]'
```

## Usage

### Command Line Interface

The command-line interface (CLI) for `git-author-stats` is suitable
for outputting stats for a repository or Github org in a tabular data format
for subsequent analysis.

```console
$ git-author-stats -h
usage: git-author-stats [-h] [-b BRANCH] [-u USER] [-p PASSWORD]
                        [--since SINCE] [--after AFTER]
                        [--before BEFORE] [--until UNTIL]
                        [-f FREQUENCY] [--delimiter DELIMITER] [-nh]
                        [-nm] [-md]
                        url [url ...]

Print author stats for a Github organization or Git repository in
CSV/TSV or markdown format

positional arguments:
  url                   Repository URL(s)

optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  A username for accessing the repository
  -p PASSWORD, --password PASSWORD
                        A password for accessing the repository
  --since SINCE         Only include contributions on or after this
                        date
  --after AFTER         Only include contributions after this date
  --before BEFORE       Only include contributions before this date
  --until UNTIL         Only include contributions on or before this
                        date
  -f FREQUENCY, --frequency FREQUENCY
                        If provided, stats will be broken down over
                        time intervals at the specified frequency. The
                        frequency should be composed of an integer and
                        unit of time (day, week, month, or year). For
                        example, all of the following are valid: "1
                        week", "1w", "2 weeks", "2weeks", "4 months",
                        or "4m".
  --delimiter DELIMITER
                        The delimiter to use for CSV/TSV output
                        (default: ',')
  -nh, --no-header      Don't print the header row (only applies to
                        CSV/TSV output)
  -nm, --no-mailmap     Don't use mailmap to map author names to email
                        addresses
  -md, --markdown       Output a markdown table instead of CSV/TSV
```

#### CLI Examples

Save weekly stats for your Github org as a CSV, authenticating using a
[personal access token](https://bit.ly/46mVout):

```bash
git-author-stats --since 2024-01-01 --frequency 1w --password $GH_TOKEN \
https://github.com/enorganic > ./enorganic-author-stats.csv
```

Save weekly stats for a Github org as a TSV (public repos only):

```bash
git-author-stats --since 2024-01-01 --frequency 1w \
--delimiter "\t" https://github.com/enorganic > ./enorganic-author-stats.tsv
```

Print daily stats for a repo from July 29th - August 1st, as a markdown table:

```bash
git-author-stats -md \
--since 2024-07-29 \
--until 2024-08-01 \
-f 1d \
https://github.com/enorganic/git-author-stats.git
```

| url                                               | since      | before     | author_date         | author_name  | commit  | file                             | insertions | deletions |
| ------------------------------------------------- | ---------- | ---------- | ------------------- | ------------ | ------- | -------------------------------- | ---------- | --------- |
| https://github.com/enorganic/git-author-stats.git | 2024-08-01 | 2024-08-02 | 2024-08-01T01:03:41 | David Belais | 7bd7967 | git_author_stats/_stats.py       | 1          | 1         |
| https://github.com/enorganic/git-author-stats.git | 2024-08-01 | 2024-08-02 | 2024-08-01T00:14:20 | David Belais | f3e837d | git_author_stats/_stats.py       | 0          | 3         |
| https://github.com/enorganic/git-author-stats.git | 2024-08-01 | 2024-08-02 | 2024-08-01T00:06:21 | David Belais | 26a2afa | README.md                        | 5          | 6         |
| https://github.com/enorganic/git-author-stats.git | 2024-08-01 | 2024-08-02 | 2024-08-01T00:01:00 | David Belais | 7461720 | git_author_stats/_stats.py       | 1          | 1         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-31 | 2024-08-01 | 2024-07-31T23:58:25 | David Belais | 5ffa426 | git_author_stats/_stats.py       | 13         | 33        |
| https://github.com/enorganic/git-author-stats.git | 2024-07-31 | 2024-08-01 | 2024-07-31T23:42:22 | David Belais | 8562114 | tests/test_stats.py              | 2          | 2         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-31 | 2024-08-01 | 2024-07-31T23:06:50 | David Belais | 4974f42 | git_author_stats/__init__.py     | 9          | 1         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-31 | 2024-08-01 | 2024-07-31T23:06:50 | David Belais | 4974f42 | git_author_stats/__main__.py     | 15         | 13        |
| https://github.com/enorganic/git-author-stats.git | 2024-07-31 | 2024-08-01 | 2024-07-31T23:06:50 | David Belais | 4974f42 | git_author_stats/_stats.py       | 120        | 52        |
| https://github.com/enorganic/git-author-stats.git | 2024-07-31 | 2024-08-01 | 2024-07-31T23:06:50 | David Belais | 4974f42 | setup.cfg                        | 1          | 1         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-31 | 2024-08-01 | 2024-07-31T23:06:50 | David Belais | 4974f42 | tests/stats.csv                  | 58983      | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-31 | 2024-08-01 | 2024-07-31T23:06:50 | David Belais | 4974f42 | tests/stats.md                   | 58984      | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-31 | 2024-08-01 | 2024-07-31T23:06:50 | David Belais | 4974f42 | tests/stats.tsv                  | 58983      | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-31 | 2024-08-01 | 2024-07-31T23:06:50 | David Belais | 4974f42 | tests/test_stats.py              | 56         | 2         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-31 | 2024-08-01 | 2024-07-31T06:47:19 | David Belais | b4a0b5f | git_author_stats/_stats.py       | 14         | 8         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-31 | 2024-08-01 | 2024-07-31T06:41:06 | David Belais | 99f59fd | git_author_stats/__init__.py     | 2          | 1         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-31 | 2024-08-01 | 2024-07-31T06:41:06 | David Belais | 99f59fd | git_author_stats/__main__.py     | 7          | 90        |
| https://github.com/enorganic/git-author-stats.git | 2024-07-31 | 2024-08-01 | 2024-07-31T06:41:06 | David Belais | 99f59fd | git_author_stats/_stats.py       | 140        | 2         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-31 | 2024-08-01 | 2024-07-31T06:41:06 | David Belais | 99f59fd | requirements.txt                 | 3          | 3         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-31 | 2024-08-01 | 2024-07-31T06:41:06 | David Belais | 99f59fd | setup.cfg                        | 1          | 1         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T22:08:36 | David Belais | c42d567 | README.md                        | 9          | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T21:52:43 | David Belais | e37df00 | git_author_stats/_stats.py       | 3          | 3         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T21:50:34 | David Belais | b06f78b | git_author_stats/_stats.py       | 4          | 6         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T21:16:44 | David Belais | 2e16532 | README.md                        | 140        | 150       |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T21:16:44 | David Belais | 2e16532 | enorganic-author-stats.csv       | 0          | 451       |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T21:16:44 | David Belais | 2e16532 | git_author_stats/__main__.py     | 33         | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T21:16:44 | David Belais | 2e16532 | git_author_stats/_stats.py       | 108        | 13        |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T18:45:33 | David Belais | 2aea5ab | setup.cfg                        | 1          | 1         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T18:43:17 | David Belais | cade4a3 | enorganic-author-stats.csv       | 451        | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T18:39:58 | David Belais | 5e99fe6 | README.md                        | 53         | 27        |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T18:39:58 | David Belais | 5e99fe6 | git_author_stats/__main__.py     | 36         | 18        |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T18:39:58 | David Belais | 5e99fe6 | tests/test_github.py             | 22         | 1         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T18:39:58 | David Belais | 5e99fe6 | tests/test_stats.py              | 20         | 1         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T04:55:31 | David Belais | b52106f | README.md                        | 3          | 2         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T04:46:42 | David Belais | 620dcdf | README.md                        | 142        | 34        |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T04:23:39 | David Belais | 282b807 | stats.ipynb                      | 0          | 177       |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T04:17:29 | David Belais | 259e788 | .flake8                          | 7          | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T04:17:29 | David Belais | 259e788 | .github/workflows/distribute.yml | 40         | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T04:17:29 | David Belais | 259e788 | .github/workflows/test.yml       | 47         | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T04:17:29 | David Belais | 259e788 | .gitignore                       | 17         | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T04:17:29 | David Belais | 259e788 | CONTRIBUTING.md                  | 56         | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T04:17:29 | David Belais | 259e788 | Makefile                         | 87         | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T04:17:29 | David Belais | 259e788 | README.md                        | 101        | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T04:17:29 | David Belais | 259e788 | ci_requirements.txt              | 2          | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T04:17:29 | David Belais | 259e788 | dev_requirements.txt             | 2          | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T04:17:29 | David Belais | 259e788 | git_author_stats/__init__.py     | 10         | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T04:17:29 | David Belais | 259e788 | git_author_stats/__main__.py     | 178        | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T04:17:29 | David Belais | 259e788 | git_author_stats/_github.py      | 53         | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T04:17:29 | David Belais | 259e788 | git_author_stats/_stats.py       | 662        | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T04:17:29 | David Belais | 259e788 | git_author_stats/py.typed        | 0          | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T04:17:29 | David Belais | 259e788 | mypy.ini                         | 5          | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T04:17:29 | David Belais | 259e788 | pyproject.toml                   | 28         | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T04:17:29 | David Belais | 259e788 | requirements.txt                 | 67         | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T04:17:29 | David Belais | 259e788 | setup.cfg                        | 27         | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T04:17:29 | David Belais | 259e788 | setup.py                         | 3          | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T04:17:29 | David Belais | 259e788 | stats.ipynb                      | 177        | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T04:17:29 | David Belais | 259e788 | test_requirements.txt            | 9          | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T04:17:29 | David Belais | 259e788 | tests/test_github.py             | 167        | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T04:17:29 | David Belais | 259e788 | tests/test_stats.py              | 166        | 0         |
| https://github.com/enorganic/git-author-stats.git | 2024-07-30 | 2024-07-31 | 2024-07-30T04:17:29 | David Belais | 259e788 | tox.ini                          | 56         | 0         |
