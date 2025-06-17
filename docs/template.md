# Template

A [cookiecutter](https://cookiecutter.readthedocs.io/en/latest/) template is
provided to kickstart your Jupyter notebook project using `git-author-stats`.
To get started using this template:

-   Install [hatch](https://hatch.pypa.io/latest/install/)

-   Install [cookiecutter](https://cookiecutter.readthedocs.io/en/latest/installation.html)

-   Execute the following command (replacing "~/Code" with the path under
    which you want to create your new project):

    ```bash
    cd ~/Code && \
    cookiecutter "https://github.com/enorganic/git-author-stats.git" --directory="template"
    ```

-   Follow the prompts to enter template fields. For example:

    ```console
    $ cookiecutter /Users/davidbelais/Code/git-author-stats/template
    [1/5]  project_name - The name of your project (example:
    organization-git-author-stats) (): pypa-git-author-stats
    [2/5] repository_url - The URL of the Git repository or organization
    (examples: github.com/organization or
    github.com/organization/organization-git-author-stats) (): github.com/pypa
    [3/5] token_environment_variable - The name of an environment variable that
    contains your GitHub developer token, if needed (example: GITHUB_PASSWORD) ():
    [4/5] initial_history_number_of_days - The number of days of commit history to
    evaluate during the initial run (default: 730, which is 2 years) (730):
    [5/5] stale_pull_request_open_days - The maximum number of days a pull request
    can be open before it is considered stale (default: 28). This will effect the
    number of overlapping days which are retrieved for subsequent notebook runs.
    (28):
    ```

    The resulting directory/file structure created by the above example input
    looks as follows:

    ```console
    $ tree -a -I '.git|.mypy_cache|.ruff_cache' pypa-git-author-stats
    pypa-git-author-stats
    ├── .editorconfig
    ├── .gitignore
    ├── Makefile
    ├── pypa-git-author-stats.ipynb
    └── pyproject.toml
    ```

-   Set the kernel for your notebook to your hatch virtual environment
    path, which can be identified by running `hatch env find` in your
    console, from your project directory.

-   In your notebook, search for "TODO:", where you will find comments
    with further instruction.

