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
                        [--since SINCE] [--after AFTER] [--before BEFORE]
                        [--until UNTIL] [-f FREQUENCY]
                        [--delimiter DELIMITER] [-nh] [-md]
                        [-rea REGULAR_EXPRESSION ALIAS]
                        [-e]
                        url [url ...]

Print author stats for a Github organization or Git repository in the format
of a Markdown table or CSV/TSV.

positional arguments:
  url                   Repository URL(s)

optional arguments:
  -h, --help            show this help message and exit
  -b BRANCH, --branch BRANCH
                        Retrieve files from BRANCH instead of the remote's
                        HEAD
  -u USER, --user USER  A username for accessing the repository
  -p PASSWORD, --password PASSWORD
                        A password for accessing the repository
  --since SINCE         Only include contributions on or after this date
  --after AFTER         Only include contributions after this date
  --before BEFORE       Only include contributions before this date
  --until UNTIL         Only include contributions on or before this date
  -f FREQUENCY, --frequency FREQUENCY
                        If provided, stats will be broken down over time
                        intervals at the specified frequency. The frequency
                        should be composed of an integer and unit of time
                        (day, week, month, or year). For example, all of the
                        following are valid: "1 week", "1w", "2 weeks",
                        "2weeks", "4 months", or "4m".
  --delimiter DELIMITER
                        The delimiter to use for CSV/TSV output (default:
                        ',')
  -nh, --no-header      Don't print the header row (only applies to CSV/TSV
                        output)
  -md, --markdown       Output a markdown table instead of CSV/TSV
  -rea REGULAR_EXPRESSION ALIAS, --regular-expression-alias REGULAR_EXPRESSION ALIAS
                        A regular expression and alias to use when an author
                        name matches the provided regular expression
  -e, --email           Include author email addresses in the output
```

#### CLI Examples

Save stats for your Github org as a CSV, authenticating using a
[personal access token](https://bit.ly/46mVout):

```bash
git-author-stats --since 2024-01-01 --frequency 1w --password $GH_TOKEN \
https://github.com/enorganic > ./enorganic-author-stats.csv
```

Save stats for a Github org as a TSV (public repos only):

```bash
git-author-stats --since 2024-01-01 --frequency 1w \
--delimiter "\t" https://github.com/enorganic > ./enorganic-author-stats.tsv
```

Print stats for a repo as a markdown table:

```bash
git-author-stats \
-md --since 2024-01-01 -f 1w \
https://github.com/enorganic/git-author-stats.git
```

| url                                               | author       | since      | before     | insertions | deletions | file                             |
| ------------------------------------------------- | ------------ | ---------- | ---------- | ---------- | --------- | -------------------------------- |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-04-29 | 2024-05-06 | 7          | 0         | .flake8                          |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-04-29 | 2024-05-06 | 40         | 0         | .github/workflows/distribute.yml |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-04-29 | 2024-05-06 | 41         | 0         | .github/workflows/test.yml       |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-04-29 | 2024-05-06 | 17         | 0         | .gitignore                       |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-04-29 | 2024-05-06 | 47         | 0         | CONTRIBUTING.md                  |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-04-29 | 2024-05-06 | 74         | 0         | Makefile                         |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-04-29 | 2024-05-06 | 10         | 0         | git_author_stats/__init__.py     |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-04-29 | 2024-05-06 | 45         | 0         | git_author_stats/__main__.py     |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-04-29 | 2024-05-06 | 47         | 0         | git_author_stats/_github.py      |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-04-29 | 2024-05-06 | 619        | 0         | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-04-29 | 2024-05-06 | 0          | 0         | git_author_stats/py.typed        |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-04-29 | 2024-05-06 | 5          | 0         | mypy.ini                         |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-04-29 | 2024-05-06 | 28         | 0         | pyproject.toml                   |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-04-29 | 2024-05-06 | 52         | 0         | requirements.txt                 |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-04-29 | 2024-05-06 | 27         | 0         | setup.cfg                        |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-04-29 | 2024-05-06 | 3          | 0         | setup.py                         |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-04-29 | 2024-05-06 | 66         | 0         | stats.ipynb                      |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-04-29 | 2024-05-06 | 4          | 0         | temp.sh                          |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-04-29 | 2024-05-06 | 13         | 0         | tests/test_github.py             |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-04-29 | 2024-05-06 | 140        | 0         | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-04-29 | 2024-05-06 | 36         | 0         | tox.ini                          |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-04-29 | 2024-05-06 | 24         | 0         | README.md                        |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-22 | 2024-07-29 | 99         | 10        | tests/test_github.py             |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-22 | 2024-07-29 | 77         | 62        | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-22 | 2024-07-29 | 24         | 18        | .github/workflows/test.yml       |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-22 | 2024-07-29 | 28         | 15        | Makefile                         |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-22 | 2024-07-29 | 224        | 202       | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-22 | 2024-07-29 | 3          | 0         | pyproject.toml                   |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-22 | 2024-07-29 | 29         | 9         | tox.ini                          |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-22 | 2024-07-29 | 3          | 1         | dev_requirements.txt             |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-22 | 2024-07-29 | 38         | 7         | stats.ipynb                      |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-22 | 2024-07-29 | 29         | 29        | tests/test_cli.py                |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-22 | 2024-07-29 | 2          | 0         | ci_requirements.txt              |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-22 | 2024-07-29 | 7          | 1         | git_author_stats/_github.py      |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-22 | 2024-07-29 | 123        | 109       | requirements.txt                 |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-22 | 2024-07-29 | 8          | 0         | test_requirements.txt            |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-22 | 2024-07-29 | 78         | 1         | README.md                        |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-22 | 2024-07-29 | 141        | 8         | git_author_stats/__main__.py     |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-22 | 2024-07-29 | 3          | 3         | setup.cfg                        |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-22 | 2024-07-29 | 15         | 6         | CONTRIBUTING.md                  |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-22 | 2024-07-29 | 0          | 4         | temp.sh                          |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-29 | 2024-07-31 | 142        | 34        | README.md                        |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-29 | 2024-07-31 | 119        | 216       | stats.ipynb                      |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-29 | 2024-07-31 | 5          | 5         | tox.ini                          |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-29 | 2024-07-31 | 33         | 12        | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-29 | 2024-07-31 | 1          | 4         | pyproject.toml                   |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-29 | 2024-07-31 | 99         | 34        | tests/test_github.py             |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-29 | 2024-07-31 | 42         | 31        | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-29 | 2024-07-31 | 1          | 0         | requirements.txt                 |
| https://github.com/enorganic/git-author-stats.git | David Belais | 2024-07-29 | 2024-07-31 | 1          | 0         | test_requirements.txt            |

Print stats for a repo as a markdown table, using an author alias:

```bash
git-author-stats \
-md --since 2024-01-01 -f 1w \
-rea '^David\s+Belais\b.*' Dave \
https://github.com/enorganic/git-author-stats.git
```

| url                                               | author | since      | before     | insertions | deletions | file                             |
| ------------------------------------------------- | ------ | ---------- | ---------- | ---------- | --------- | -------------------------------- |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-04-29 | 2024-05-06 | 7          | 0         | .flake8                          |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-04-29 | 2024-05-06 | 40         | 0         | .github/workflows/distribute.yml |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-04-29 | 2024-05-06 | 41         | 0         | .github/workflows/test.yml       |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-04-29 | 2024-05-06 | 17         | 0         | .gitignore                       |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-04-29 | 2024-05-06 | 47         | 0         | CONTRIBUTING.md                  |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-04-29 | 2024-05-06 | 74         | 0         | Makefile                         |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-04-29 | 2024-05-06 | 10         | 0         | git_author_stats/__init__.py     |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-04-29 | 2024-05-06 | 45         | 0         | git_author_stats/__main__.py     |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-04-29 | 2024-05-06 | 47         | 0         | git_author_stats/_github.py      |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-04-29 | 2024-05-06 | 619        | 0         | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-04-29 | 2024-05-06 | 0          | 0         | git_author_stats/py.typed        |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-04-29 | 2024-05-06 | 5          | 0         | mypy.ini                         |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-04-29 | 2024-05-06 | 28         | 0         | pyproject.toml                   |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-04-29 | 2024-05-06 | 52         | 0         | requirements.txt                 |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-04-29 | 2024-05-06 | 27         | 0         | setup.cfg                        |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-04-29 | 2024-05-06 | 3          | 0         | setup.py                         |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-04-29 | 2024-05-06 | 66         | 0         | stats.ipynb                      |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-04-29 | 2024-05-06 | 4          | 0         | temp.sh                          |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-04-29 | 2024-05-06 | 13         | 0         | tests/test_github.py             |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-04-29 | 2024-05-06 | 140        | 0         | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-04-29 | 2024-05-06 | 36         | 0         | tox.ini                          |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-04-29 | 2024-05-06 | 24         | 0         | README.md                        |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-22 | 2024-07-29 | 99         | 10        | tests/test_github.py             |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-22 | 2024-07-29 | 77         | 62        | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-22 | 2024-07-29 | 24         | 18        | .github/workflows/test.yml       |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-22 | 2024-07-29 | 28         | 15        | Makefile                         |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-22 | 2024-07-29 | 224        | 202       | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-22 | 2024-07-29 | 3          | 0         | pyproject.toml                   |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-22 | 2024-07-29 | 29         | 9         | tox.ini                          |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-22 | 2024-07-29 | 3          | 1         | dev_requirements.txt             |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-22 | 2024-07-29 | 38         | 7         | stats.ipynb                      |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-22 | 2024-07-29 | 29         | 29        | tests/test_cli.py                |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-22 | 2024-07-29 | 2          | 0         | ci_requirements.txt              |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-22 | 2024-07-29 | 7          | 1         | git_author_stats/_github.py      |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-22 | 2024-07-29 | 123        | 109       | requirements.txt                 |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-22 | 2024-07-29 | 8          | 0         | test_requirements.txt            |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-22 | 2024-07-29 | 78         | 1         | README.md                        |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-22 | 2024-07-29 | 141        | 8         | git_author_stats/__main__.py     |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-22 | 2024-07-29 | 3          | 3         | setup.cfg                        |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-22 | 2024-07-29 | 15         | 6         | CONTRIBUTING.md                  |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-22 | 2024-07-29 | 0          | 4         | temp.sh                          |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-29 | 2024-07-31 | 142        | 34        | README.md                        |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-29 | 2024-07-31 | 119        | 216       | stats.ipynb                      |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-29 | 2024-07-31 | 5          | 5         | tox.ini                          |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-29 | 2024-07-31 | 33         | 12        | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-29 | 2024-07-31 | 1          | 4         | pyproject.toml                   |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-29 | 2024-07-31 | 99         | 34        | tests/test_github.py             |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-29 | 2024-07-31 | 42         | 31        | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-29 | 2024-07-31 | 1          | 0         | requirements.txt                 |
| https://github.com/enorganic/git-author-stats.git | Dave   | 2024-07-29 | 2024-07-31 | 1          | 0         | test_requirements.txt            |
