import re
from re import Pattern

PROJECT_NAME_REGEX: str = r"^[a-z][a-z0-9\-]*[a-z0-9]$"
PROJECT_NAME_PATTERN: Pattern = re.compile(PROJECT_NAME_REGEX)
PROJECT_NAME: str = "{{cookiecutter.project_name}}"


def main() -> None:
    message: str
    if not PROJECT_NAME_PATTERN.match(PROJECT_NAME):
        message = (
            f"{PROJECT_NAME!r} is not a valid project name. "
            "Project names must match the following regular expression: "
            f"{PROJECT_NAME_REGEX!r}"
        )
        raise ValueError(message)


if __name__ == "__main__":
    main()
