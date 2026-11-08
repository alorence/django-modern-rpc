# ruff: noqa: T201, S603, S607
"""Mechanical pre-release checks for django-modern-rpc (stdlib only).

Usage: python3 .claude/skills/release-checks/scripts/check_release.py

Prints one line per check, prefixed by [OK], [WARN] or [FAIL], and exits with status 1 if any check failed.
The test matrix (source of truth for supported Python / Django versions) is read from `uvx nox -l`.
"""

from __future__ import annotations

import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PACKAGE = "django-modern-rpc"

results: list[tuple[str, str]] = []


def report(status: str, message: str) -> None:
    results.append((status, message))
    print(f"[{status}] {message}")


def check(condition: bool, ok_msg: str, fail_msg: str, *, fail_status: str = "FAIL") -> None:
    report("OK", ok_msg) if condition else report(fail_status, fail_msg)


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False).stdout.strip()


def vkey(version: str) -> tuple[int, ...]:
    return tuple(int(p) for p in version.split("."))


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


# ---------------------------------------------------------------- versions
pyproject = read("pyproject.toml")
match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject, re.MULTILINE)
if not match:
    report("FAIL", "Unable to find project version in pyproject.toml")
    sys.exit(1)
version = match.group(1)
print(f"pyproject.toml version: {version}\n")

changelog = read("CHANGELOG.md")
first_section = re.search(r"^## (.+)$", changelog, re.MULTILINE)
heading = first_section.group(1).strip() if first_section else "<none>"
check(
    heading == f"v{version}",
    f"CHANGELOG.md first section is '## v{version}'",
    f"CHANGELOG.md first section is '## {heading}', expected '## v{version}'",
)

if first_section:
    body = changelog[first_section.end() :]
    next_section = re.search(r"^## ", body, re.MULTILINE)
    body = body[: next_section.start()] if next_section else body
    date_match = re.search(r"\*\*Release date: ([^*]+)\*\*", body)
    raw_date = date_match.group(1).strip() if date_match else "<missing>"
    try:
        release_date = dt.date.fromisoformat(raw_date)
    except ValueError:
        report("FAIL", f"CHANGELOG.md release date is '{raw_date}', expected an ISO date (YYYY-MM-DD)")
    else:
        check(
            release_date == dt.date.today(),
            f"CHANGELOG.md release date is today ({release_date})",
            f"CHANGELOG.md release date is {release_date}, not today",
            fail_status="WARN",
        )
    check(
        bool(re.search(r"^- ", body, re.MULTILINE)),
        "CHANGELOG.md release section has entries",
        "CHANGELOG.md release section has no entry",
    )

lock_match = re.search(rf'^name = "{PACKAGE}"\nversion = "([^"]+)"', read("uv.lock"), re.MULTILINE)
lock_version = lock_match.group(1) if lock_match else "<missing>"
check(
    lock_version == version,
    "uv.lock project version matches",
    f"uv.lock project version is {lock_version} (run `uv lock`)",
)

# ---------------------------------------------------------------- git
check(
    not git("tag", "--list", version),
    f"Tag {version} does not exist yet",
    f"Tag {version} already exists",
)
previous_tags = sorted(
    (t for t in git("tag", "--list").splitlines() if re.fullmatch(r"\d+\.\d+\.\d+", t)),
    key=vkey,
)
if previous_tags and re.fullmatch(r"\d+\.\d+\.\d+", version):
    check(
        vkey(version) > vkey(previous_tags[-1]),
        f"Version {version} is greater than latest tag {previous_tags[-1]}",
        f"Version {version} is not greater than latest tag {previous_tags[-1]}",
    )
check(not git("status", "--porcelain"), "Working tree is clean", "Working tree is not clean")
branch = git("rev-parse", "--abbrev-ref", "HEAD")
check(branch == "main", "Current branch is main", f"Current branch is {branch}, not main", fail_status="WARN")
git("fetch", "--quiet", "origin")
behind = git("rev-list", "--count", "HEAD..origin/main") or "?"
check(behind == "0", "HEAD is up to date with origin/main", f"HEAD is {behind} commit(s) behind origin/main")

# ---------------------------------------------------------------- supported versions
nox = subprocess.run(["uvx", "nox", "-l"], cwd=ROOT, capture_output=True, text=True, check=False)
matrix = {
    (py, dj) for py, dj in re.findall(r"^\* tests\(Python ([\d.]+) \S+ Django ([\d.]+)\)", nox.stdout, re.MULTILINE)
}
if not matrix:
    report("FAIL", f"Unable to read the test matrix from `uvx nox -l`:\n{nox.stderr}")
else:
    pythons = sorted({py for py, _ in matrix}, key=vkey)
    djangos = sorted({dj for _, dj in matrix}, key=vkey)
    print(f"\nnox matrix: Python {', '.join(pythons)} / Django {', '.join(djangos)}\n")

    # README table
    readme = read("README.md")
    header = re.search(r"^\|\s*Python\s*\S*\s*\|(.+)\|\s*$", readme, re.MULTILINE)
    if not header:
        report("FAIL", "README.md: Python / Django support table not found")
    else:
        readme_pythons = [c.strip() for c in header.group(1).split("|")]
        rows = re.findall(r"^\|\s*Django ([\d.]+)\s*\|(.+)\|\s*$", readme, re.MULTILINE)
        readme_matrix = set()
        for dj, cells in rows:
            for py, cell in zip(readme_pythons, cells.split("|"), strict=False):
                if "🟢" in cell:
                    readme_matrix.add((py, dj))
        check(
            readme_pythons == pythons,
            "README.md table columns match nox Python versions",
            f"README.md table columns {readme_pythons} != nox Python versions {pythons}",
        )
        check(
            [dj for dj, _ in rows] == djangos,
            "README.md table rows match nox Django versions",
            f"README.md table rows {[dj for dj, _ in rows]} != nox Django versions {djangos}",
        )
        diff = sorted(readme_matrix ^ matrix)
        check(
            not diff,
            "README.md table cells match nox test matrix",
            f"README.md table cells differ from nox matrix for (python, django): {diff}",
        )

    # pyproject classifiers and lower bounds
    py_classifiers = sorted(re.findall(r'"Programming Language :: Python :: (3\.\d+)"', pyproject), key=vkey)
    dj_classifiers = sorted(re.findall(r'"Framework :: Django :: ([\d.]+)"', pyproject), key=vkey)
    check(
        py_classifiers == pythons,
        "pyproject.toml Python classifiers match nox matrix",
        f"pyproject.toml Python classifiers {py_classifiers} != {pythons}",
    )
    check(
        dj_classifiers == djangos,
        "pyproject.toml Django classifiers match nox matrix",
        f"pyproject.toml Django classifiers {dj_classifiers} != {djangos}",
    )
    requires_python = re.search(r'^requires-python\s*=\s*">=\s*([\d.]+)"', pyproject, re.MULTILINE)
    check(
        bool(requires_python) and requires_python.group(1) == pythons[0],
        f"requires-python lower bound is {pythons[0]}",
        f"requires-python lower bound should be {pythons[0]}",
    )
    django_dep = re.search(r'"django\s*>=\s*([\d.]+)"', pyproject)
    check(
        bool(django_dep) and django_dep.group(1) == djangos[0],
        f"django dependency lower bound is {djangos[0]}",
        f"django dependency lower bound should be {djangos[0]}",
    )
    docs_req = re.search(r"requires Python ([\d.]+)\+ and Django ([\d.]+)\+", read("docs/index.rst"))
    check(
        bool(docs_req) and docs_req.groups() == (pythons[0], djangos[0]),
        "docs/index.rst minimal Python / Django versions are correct",
        f"docs/index.rst should state 'requires Python {pythons[0]}+ and Django {djangos[0]}+'",
    )

# ---------------------------------------------------------------- copyright years
year = str(dt.date.today().year)
check(
    bool(re.search(rf"Copyright © \d{{4}}-{year} ", read("LICENSE.txt"))),
    f"LICENSE.txt copyright ends with {year}",
    f"LICENSE.txt copyright should end with {year}",
)
check(
    f'project_copyright = "{year}"' in read("docs/conf.py"),
    f"docs/conf.py project_copyright is {year}",
    f"docs/conf.py project_copyright should be {year}",
)

# ---------------------------------------------------------------- summary
fails = sum(1 for status, _ in results if status == "FAIL")
warns = sum(1 for status, _ in results if status == "WARN")
print(f"\n{len(results)} checks: {fails} failure(s), {warns} warning(s)")
sys.exit(1 if fails else 0)
