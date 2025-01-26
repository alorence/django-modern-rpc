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

    if dj == Django.v5_1:
        return Version("3.10") <= py <= Version("3.13")

    return False


test_matrix = [(python, django) for python in Python for django in Django if is_combination_supported(python, django)]
session_ids = [f"py{py.replace('.', '')}-dj{dj.replace('.', '')}" for py, dj in test_matrix]


@nox.session(venv_backend="uv")
@nox.parametrize(["python", "django"], test_matrix, ids=session_ids)
def tests(session, python, django):
    env = {"UV_PROJECT_ENVIRONMENT": session.virtualenv.location}
    session.run_install("uv", "sync", "-p", python, "--no-group", "django", env=env)
    session.install(f"django=={django}.*")

    session.run("django-admin", "--version")
    post_args = session.posargs or []
    session.run("pytest", "-n", "auto", *post_args)


@nox.session(name="ruff-lint", venv_backend=None)
def ruff_lint(session):
    session.run("uv", "run", "ruff", "check", ".")


@nox.session(name="ruff-format", venv_backend=None)
def ruff_format(session):
    session.run("uv", "run", "ruff", "format", ".", "--check")


@nox.session(venv_backend=None)
def mypy(session):
    session.run("uv", "run", "mypy", ".")


@nox.session(venv_backend=None, default=False)
def coverage(session):
    session.run("uv", "run", "pytest", "--cov=modernrpc", "--cov-report=html")
