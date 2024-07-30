# git-author-stats

[![test](https://github.com/enorganic/git-author-stats/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/enorganic/git-author-stats/actions/workflows/test.yml)
[![distribute](https://github.com/enorganic/git-author-stats/actions/workflows/distribute.yml/badge.svg?branch=main)](https://github.com/enorganic/git-author-stats/actions/workflows/distribute.yml)

This package provides a CLI and library for compiling author stats for a Git
repository or Github organization.

## Installation

You can install `git-author-stats` with pip:

```shell
pip3 install git-author-stats
```

## Usage

### Command Line Interface

The command-line interface for `git-author-stats`

```console
$ git-author-stats -h
usage: git-author-stats [-h] [-b BRANCH] [-u USER] [-p PASSWORD]
                        [--since SINCE] [--after AFTER]
                        [--before BEFORE] [--until UNTIL]
                        [-f FREQUENCY] [--delimiter DELIMITER]
                        url [url ...]

Retrieve author stats for a Github organization or Git
repository.

positional arguments:
  url                   Repository URL(s)

optional arguments:
  -h, --help            show this help message and exit
  -b BRANCH, --branch BRANCH
                        Retrieve files from BRANCH instead of
                        the remote's HEAD
  -u USER, --user USER  A username for accessing the repository
  -p PASSWORD, --password PASSWORD
                        A password for accessing the repository
  --since SINCE         Only include contributions on or after
                        this date
  --after AFTER         Only include contributions after this
                        date
  --before BEFORE       Only include contributions before this
                        date
  --until UNTIL         Only include contributions on or before
                        this date
  -f FREQUENCY, --frequency FREQUENCY
                        If provided, stats will be broken down
                        over time intervals at the specified
                        frequency. The frequency should be
                        composed of an integer and unit of time
                        (day, week, month, or year). For
                        example, all of the following are valid:
                        "1 week", "1w", "2 weeks", "2weeks", "4
                        months", or "4m".
  --delimiter DELIMITER
```

#### Examples

Save stats for an org as a CSV:

```bash
git-author-stats --since 2024-01-01 --frequency 1w --password $GH_PASSWORD \
--delimiter , https://github.com/enorganic > ./enorganic-author-stats.csv
```

Print stats for a repo as a markdown table:

```bash
git-author-stats --since 2024-01-01 -f 1w https://github.com/enorganic/git-author-stats.git
```

| url                                               | author                         | since      | before     | insertions | deletions | file                             |
| ------------------------------------------------- | ------------------------------ | ---------- | ---------- | ---------- | --------- | -------------------------------- |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 7          | 0         | .flake8                          |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 40         | 0         | .github/workflows/distribute.yml |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 41         | 0         | .github/workflows/test.yml       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 17         | 0         | .gitignore                       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 47         | 0         | CONTRIBUTING.md                  |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 74         | 0         | Makefile                         |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 10         | 0         | git_author_stats/__init__.py     |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 45         | 0         | git_author_stats/__main__.py     |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 47         | 0         | git_author_stats/_github.py      |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 619        | 0         | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 0          | 0         | git_author_stats/py.typed        |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 5          | 0         | mypy.ini                         |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 28         | 0         | pyproject.toml                   |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 52         | 0         | requirements.txt                 |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 27         | 0         | setup.cfg                        |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 3          | 0         | setup.py                         |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 66         | 0         | stats.ipynb                      |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 4          | 0         | temp.sh                          |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 13         | 0         | tests/test_github.py             |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 140        | 0         | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 36         | 0         | tox.ini                          |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 24         | 0         | README.md                        |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 0         | tox.ini                          |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 33         | 12        | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 0          | 3         | pyproject.toml                   |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 0          | 1         | tests/test_github.py             |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 0          | 2         | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 0          | 12        | tests/test_github.py             |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 0          | 6         | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 3         | tox.ini                          |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 4          | 4         | tests/test_github.py             |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 1         | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 2         | tox.ini                          |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 2          | 2         | tests/test_github.py             |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 3          | 2         | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 1         | pyproject.toml                   |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 0         | requirements.txt                 |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 119        | 39        | stats.ipynb                      |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 0         | test_requirements.txt            |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 93         | 15        | tests/test_github.py             |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 38         | 20        | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 2          | 0         | tox.ini                          |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 4          | 0         | tests/test_github.py             |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 5          | 0         | tests/test_github.py             |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 4          | 0         | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 2          | 7         | .github/workflows/test.yml       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 2          | 2         | Makefile                         |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 2          | 2         | .github/workflows/test.yml       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 2          | 2         | Makefile                         |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 15        | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 3          | 0         | pyproject.toml                   |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 4          | 2         | tox.ini                          |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 2          | 2         | .github/workflows/test.yml       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 2          | 1         | .github/workflows/test.yml       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 0         | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 2          | 1         | dev_requirements.txt             |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 27         | 8         | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 38         | 7         | stats.ipynb                      |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 4          | 4         | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 2          | 2         | tox.ini                          |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 1         | .github/workflows/test.yml       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 0         | .github/workflows/test.yml       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 64         | 84        | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 2          | 2         | tests/test_github.py             |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 1         | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 1         | .github/workflows/test.yml       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 1         | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 3          | 0         | tox.ini                          |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 0          | 1         | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 2          | 2         | tests/test_github.py             |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 1         | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 4          | 0         | .github/workflows/test.yml       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 1         | Makefile                         |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 9          | 12        | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 0          | 28        | tests/test_cli.py                |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 55         | 0         | tests/test_github.py             |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 22         | 33        | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 10         | 4         | tox.ini                          |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 17         | 12        | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 1         | tests/test_github.py             |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 1         | tox.ini                          |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 8          | 3         | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 1         | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 2          | 1         | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 0         | tests/test_cli.py                |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 5          | 3         | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 2          | 1         | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 8          | 2         | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 1         | tests/test_cli.py                |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 3          | 1         | .github/workflows/test.yml       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 22         | 14        | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 2          | 1         | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 5          | 3         | tests/test_github.py             |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 6          | 4         | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 1         | .github/workflows/test.yml       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 9          | 2         | tests/test_github.py             |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 3         | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 3          | 0         | tox.ini                          |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 8          | 2         | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 2          | 0         | .github/workflows/test.yml       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 23         | 10        | Makefile                         |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 2          | 0         | ci_requirements.txt              |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 0         | dev_requirements.txt             |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 7          | 1         | git_author_stats/_github.py      |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 15         | 26        | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 6          | 86        | requirements.txt                 |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 8          | 0         | test_requirements.txt            |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 16         | 0         | tests/test_github.py             |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 17         | 7         | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 78         | 1         | README.md                        |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 141        | 8         | git_author_stats/__main__.py     |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 33         | 14        | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 27         | 0         | tests/test_cli.py                |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 6          | 1         | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 1         | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 3         | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 3          | 1         | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 4          | 0         | tox.ini                          |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 0         | tox.ini                          |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 1         | setup.cfg                        |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 3          | 2         | .github/workflows/test.yml       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 15         | 6         | CONTRIBUTING.md                  |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 4         | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 117        | 23        | requirements.txt                 |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 2          | 2         | setup.cfg                        |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 0          | 4         | temp.sh                          |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 7          | 0         | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | David Belais <david@belais.me> | 2024-07-22 | 2024-07-29 | 1          | 0         | tox.ini                          |
