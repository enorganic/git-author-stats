# git-author-stats

[![test](https://github.com/enorganic/git-author-stats/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/enorganic/git-author-stats/actions/workflows/test.yml)
[![PyPI version](https://badge.fury.io/py/gittable.svg?icon=si%3Apython)](https://badge.fury.io/py/git-author-stats)

This package provides a CLI and library for extracting author "stats"
(insertions and deletions) for a Git repository or Github organization.

- [Contributing](https://git-author-stats.enorganic.org/contributing)
- [Report a Bug](https://github.com/enorganic/git-author-stats/issues)

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
