from __future__ import annotations

import shutil
from enum import StrEnum
from pathlib import Path

import nox
from packaging.version import Version

PROJECT_DIR = Path(__file__).parent
BENCHMARK_DIR = PROJECT_DIR / "tests" / "benchmarks"
DOCS_SRC_DIR = PROJECT_DIR / "docs"
DOCS_BUILD_DIR = PROJECT_DIR / "dist" / "docs"
AUTODOC_PORT = 8001


class Python(StrEnum):
    v3_14 = "3.14"
    v3_13 = "3.13"
    v3_12 = "3.12"
    v3_11 = "3.11"
    v3_10 = "3.10"
    v3_9 = "3.9"
    v3_8 = "3.8"

    @property
    def tag(self):
        return f"py{self.value.replace('.', '')}"


class Django(StrEnum):
    v5_2 = "5.2"
    v5_1 = "5.1"
    v5_0 = "5.0"
    v4_2 = "4.2"
    v4_1 = "4.1"
    v4_0 = "4.0"
    v3_2 = "3.2"

    @property
    def tag(self):
        return f"dj{self.value.replace('.', '')}"


def is_combination_supported(py: Python, dj: Django) -> bool:
    """Determines if the given Python / Django versions combination is supported.

    This is a direct implementation of the table provided in Django FAQ:
     - https://docs.djangoproject.com/en/5.1/faq/install/#what-python-version-can-i-use-with-django
    """
    if dj <= Django.v4_0:
        return Version(py) <= Version("3.10")

    if dj == Django.v4_1:
        return Version(py) <= Version("3.11")

    if dj == Django.v4_2:
        return Version(py) <= Version("3.12")

    if dj == Django.v5_0:
        return Version("3.10") <= Version(py) <= Version("3.12")

    if dj >= Django.v5_1:
        return Version("3.10") <= Version(py)

    return False


def is_test_enabled_on_cicd(py: Python):
    # Use this to filter out some Python version from CICD
    return True


def build_test_matrix():
    for py in Python:
        for dj in Django:
            if not is_combination_supported(py, dj):
                continue
            tags = ["tests", py.tag, dj.tag]
            if is_test_enabled_on_cicd(py):
                tags.append("cicd-tests")
            session_id = f"Python {py} × Django {dj}"  # noqa: RUF001, RUF003 (disable warning about ambiguous × char)
            yield nox.param(py, dj, id=session_id, tags=tags)


@nox.session(name="tests", venv_backend="uv")
@nox.parametrize(["python", "django"], build_test_matrix())
def tests(session, python, django):
    """Execute test suite using pytest"""
    env = {"UV_PROJECT_ENVIRONMENT": session.virtualenv.location}
    session.run_install("uv", "sync", "-p", python, "--no-install-package", "django", env=env)
    session.install(f"django=={django}.*", "--prerelease=allow")

    session.run("django-admin", "--version")
    post_args = session.posargs or []
    # Benchmarks cannot be run with parallelization enabled, run tests & benchmarks separately
    session.run("pytest", "-n", "auto", *post_args)


@nox.session(name="tests:current-venv", venv_backend="none", default=False)
def tests_current_venv(session):
    """Run tests in the current virtualenv only"""
    post_args = session.posargs or []
    session.run("uv", "run", "pytest", "-n", "auto", *post_args)


@nox.session(name="tests:coverage", venv_backend="none", default=False, tags=["tests"])
def coverage(session):
    """Run tests and generate a coverage report (in terminal by default, or in format passed as posarg)"""
    cov_type = "term"
    if session.posargs:
        cov_type = session.posargs.pop(0)
        allowed_cov_types = ("term", "term-missing", "annotate", "html", "xml", "json", "markdown", "lcov")
        if cov_type not in allowed_cov_types:
            raise ValueError(f"Invalid coverage report type {cov_type}, possible values are {allowed_cov_types}")
    session.run("uv", "run", "pytest", "-n", "auto", "--cov", f"--cov-report={cov_type}", *session.posargs)


@nox.session(name="tests:duration", venv_backend="none", default=False, tags=["tests"])
def tests_duration(session):
    """Run tests and report the 20 slowest tests"""
    session.run("uv", "run", "pytest", "--durations=20")


bench_ids = [f"Python {py}" for py in Python if is_test_enabled_on_cicd(py)]
bench_tags = [[py.tag] for py in Python if is_test_enabled_on_cicd(py)]


@nox.session(name="benchmarks", venv_backend="uv", default=False, tags=["benchmarks"])
@nox.parametrize(["python"], bench_ids, tags=bench_tags)
def benchmarks(session, python):
    """Run benchmarks on all supported Python versions"""
    env = {"UV_PROJECT_ENVIRONMENT": session.virtualenv.location}
    session.run_install("uv", "sync", "-p", python, env=env)
    session.run("pytest", BENCHMARK_DIR, "--benchmark-enable")


@nox.session(name="benchmarks:current-venv", venv_backend="none", default=False, tags=["benchmarks"])
def benchmarks_current_venv(session):
    """Run benchmarks in the current virtualenv only"""
    session.run("uv", "run", "pytest", BENCHMARK_DIR, "--benchmark-enable")


@nox.session(name="lint", venv_backend="none", tags=["ruff", "checks"])
def lint(session):
    """Check the project for common issues"""
    session.run("uv", "run", "ruff", "check", ".")


@nox.session(name="lint:fix", venv_backend="none", default=False, tags=["ruff"])
def lint_fix(session):
    """Check the project for common issues and apply obvious fixes"""
    session.run("uv", "run", "ruff", "check", ".", "--fix")


@nox.session(name="format", venv_backend="none", default=False, tags=["ruff", "checks"])
def format_apply(session):
    """Apply formatting rules on all files"""
    session.run("uv", "run", "ruff", "format", ".")


@nox.session(name="format:check", venv_backend="none", tags=["ruff", "checks"])
def format_check(session):
    """Check that all files are well formated"""
    session.run("uv", "run", "ruff", "format", ".", "--check")


@nox.session(venv_backend="uv", tags=["checks"])
def mypy(session):
    """Verify type hints"""
    env_vars = {"UV_PROJECT_ENVIRONMENT": session.virtualenv.location}
    session.run_install("uv", "sync", "--group", "type-checking", env=env_vars)
    session.run("mypy", ".", env=env_vars)


@nox.session(name="docs:build", venv_backend="uv", default=False)
def docs_build(session):
    """Build the project's documentation"""
    env_vars = {"UV_PROJECT_ENVIRONMENT": session.virtualenv.location}
    session.run_install("uv", "sync", "--group", "docs", env=env_vars)
    session.run("sphinx-build", DOCS_SRC_DIR, DOCS_BUILD_DIR, *session.posargs, env=env_vars)


@nox.session(name="docs:serve", venv_backend="uv", default=False)
def docs_serve(session):
    """Continuously rebuild the project's documentation and serve it on localhost:8001"""
    env_vars = {"UV_PROJECT_ENVIRONMENT": session.virtualenv.location}
    session.run_install("uv", "sync", "--group", "docs", env=env_vars)
    session.run(
        "sphinx-autobuild",
        "-b",
        "html",
        "--port",
        str(AUTODOC_PORT),
        DOCS_SRC_DIR,
        DOCS_BUILD_DIR,
        *session.posargs,
        env=env_vars,
    )


@nox.session(name="docs:clean", venv_backend="none", default=False)
def docs_cleanup(session):
    """Cleanup previously built docs files"""
    shutil.rmtree(DOCS_BUILD_DIR)
