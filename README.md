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

```console
$ git-author-stats --since 2024-01-01 -f 1w https://github.com/enorganic/git-author-stats.git
| url                                               | author                   | since      | before     | insertions | deletions | file                             |
| ------------------------------------------------- | -------------------------| ---------- | ---------- | ---------- | --------- | -------------------------------- |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 7          | 0         | .flake8                          |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 40         | 0         | .github/workflows/distribute.yml |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 41         | 0         | .github/workflows/test.yml       |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 17         | 0         | .gitignore                       |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 47         | 0         | CONTRIBUTING.md                  |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 74         | 0         | Makefile                         |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 10         | 0         | git_author_stats/__init__.py     |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 45         | 0         | git_author_stats/__main__.py     |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 47         | 0         | git_author_stats/_github.py      |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 619        | 0         | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 0          | 0         | git_author_stats/py.typed        |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 5          | 0         | mypy.ini                         |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 28         | 0         | pyproject.toml                   |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 52         | 0         | requirements.txt                 |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 27         | 0         | setup.cfg                        |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 3          | 0         | setup.py                         |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 66         | 0         | stats.ipynb                      |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 4          | 0         | temp.sh                          |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 13         | 0         | tests/test_github.py             |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 140        | 0         | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 36         | 0         | tox.ini                          |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-04-29 | 2024-05-06 | 24         | 0         | README.md                        |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-07-22 | 2024-07-26 | 3          | 2         | .github/workflows/test.yml       |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-07-22 | 2024-07-26 | 15         | 6         | CONTRIBUTING.md                  |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-07-22 | 2024-07-26 | 1          | 4         | git_author_stats/_stats.py       |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-07-22 | 2024-07-26 | 117        | 23        | requirements.txt                 |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-07-22 | 2024-07-26 | 2          | 2         | setup.cfg                        |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-07-22 | 2024-07-26 | 0          | 4         | temp.sh                          |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-07-22 | 2024-07-26 | 7          | 0         | tests/test_stats.py              |
| https://github.com/enorganic/git-author-stats.git | Belais <david@belais.me> | 2024-07-22 | 2024-07-26 | 1          | 0         | tox.ini                          |
```
