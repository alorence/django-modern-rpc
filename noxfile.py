from enum import StrEnum

import nox
from packaging.version import Version


class Python(StrEnum):
    v3_13 = "3.13"
    v3_12 = "3.12"
    v3_11 = "3.11"
    v3_10 = "3.10"
    v3_9 = "3.9"
    v3_8 = "3.8"


class Django(StrEnum):
    v5_2 = "5.2"
    v5_1 = "5.1"
    v5_0 = "5.0"
    v4_2 = "4.2"
    v4_1 = "4.1"
    v4_0 = "4.0"
    v3_2 = "3.2"


def is_combination_supported(py: str, dj: str) -> bool:
    """Determines if the given Python / Django versions combination is supported.

    This is a direct implementation of the table provided in Django FAQ:
     - https://docs.djangoproject.com/en/5.1/faq/install/#what-python-version-can-i-use-with-django
    """
    py = Version(py)

    if dj == Django.v3_2:
        return Version("3.6") <= py <= Version("3.10")

    if dj == Django.v4_0:
        return Version("3.8") <= py <= Version("3.10")

    if dj == Django.v4_1:
        return Version("3.8") <= py <= Version("3.11")

    if dj == Django.v4_2:
        return Version("3.8") <= py <= Version("3.12")

    if dj == Django.v5_0:
        return Version("3.10") <= py <= Version("3.12")

    if dj in (Django.v5_1, Django.v5_2):
        return Version("3.10") <= py <= Version("3.13")

    return False


def build_test_matrix():
    for py in Python:
        for dj in Django:
            if not is_combination_supported(py, dj):
                continue
            tags = [f"py{py.replace('.', '')}", f"dj{dj.replace('.', '')}", "tests"]
            session_id = f"Python {py} × Django {dj}"  # noqa: RUF001, RUF003 (disable warning about ambiguous × char)
            yield nox.param(py, dj, id=session_id, tags=tags)


@nox.session(name="test", venv_backend="uv")
@nox.parametrize(["python", "django"], build_test_matrix())
def run_tests(session, python, django):
    """Execute test suite using pytest"""
    env = {"UV_PROJECT_ENVIRONMENT": session.virtualenv.location}
    session.run_install("uv", "sync", "-p", python, "--no-install-package", "django", env=env)
    session.install(f"django=={django}.*", "--prerelease=allow")

    session.run("django-admin", "--version")
    post_args = session.posargs or []
    session.run("pytest", "-n", "auto", *post_args)


@nox.session(name="lint", venv_backend="none", tags=["ruff"])
def ruff_lint(session):
    """Check the project for common issues"""
    session.run("uv", "run", "ruff", "check", ".")


@nox.session(name="format", venv_backend="none", tags=["ruff"])
def ruff_format(session):
    """Check that all files are well formated"""
    session.run("uv", "run", "ruff", "format", ".", "--check")


@nox.session(venv_backend="uv")
def mypy(session):
    """Verify type hints"""
    env = {"UV_PROJECT_ENVIRONMENT": session.virtualenv.location}
    session.run_install("uv", "sync", "--group", "type-checking", env=env)
    session.run("mypy", ".", env=env)


@nox.session(venv_backend="none", default=False, tags=["tests"])
def cov(session):
    """Run tests and generate coverage report in 'htmlcov' directory"""
    cov_type = "term"
    if session.posargs:
        cov_type = session.posargs.pop(0)
        allowed_cov_types = ("term", "term-missing", "annotate", "html", "xml", "json", "lcov")
        if cov_type not in allowed_cov_types:
            raise ValueError(f"Invalid coverage report type {cov_type}, possible values are {allowed_cov_types}")
    session.run("uv", "run", "pytest", "--cov=modernrpc", f"--cov-report={cov_type}", *session.posargs)


@nox.session(venv_backend="none", default=False, tags=["tests"])
def tests_duration(session):
    """Run tests and report the 20 slowest tests"""
    session.run("uv", "run", "pytest", "--durations=20")
