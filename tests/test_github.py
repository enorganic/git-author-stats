import pytest

from git_author_stats._github import iter_organization_repository_clone_urls


def test_iter_organization_repository_clone_urls() -> None:
    assert "https://github.com/enorganic/dependence.git" in (
        iter_organization_repository_clone_urls("github.com/enorganic")
    )


if __name__ == "__main__":
    pytest.main(["-s", "-vv", __file__])
