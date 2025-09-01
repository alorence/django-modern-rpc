Project-specific development guidelines for django-modern-rpc

Audience: advanced contributors to this codebase. Focus is on repo-specific tooling and practices.

1) Toolchain and environment
- Package/build: uv_build backend (pyproject [build-system]). Build artifacts with: uv build
- Environment manager: uv is used directly and via nox (venv_backend="uv").
- Python/Django matrix: See noxfile.py. Supported Python versions: 3.8–3.14. Django versions: 3.2–5.2. Matrix validity is enforced by is_combination_supported(), mirroring Django’s official support table.
- Default extras/groups installed by uv: [tool.uv]. default-groups = ["dev", "tests"]. Running uv sync installs runtime deps plus dev and tests groups.

2) Base setup
- Prereq: Python ≥ 3.8 with uv installed.
- Sync dependencies for local dev:
  - uv sync
  - Notes:
    - This installs pytest, pytest-django, xdist, asyncio, cov, benchmark, sugar, ruff, etc. per [dependency-groups].
    - The Django version installed by default comes from the project dependency constraint (django >= 3.2) and resolver; to test multiple Django versions/pydirs, use nox (below).

3) Running tests (pytest directly)
- Pytest config is in pyproject ([tool.pytest.ini_options]):
  - testpaths = ["tests"], python_files = ["test_*.py", "bench_*.py"].
  - DJANGO_SETTINGS_MODULE = tests.project.settings (pytest-django managed test project).
  - asyncio_mode = auto; asyncio_default_fixture_loop_scope = session.
  - addopts includes --benchmark-disable. Benchmarks are disabled unless explicitly enabled.
- Typical invocations:
  - Run full suite in current venv: uv run pytest -n auto
  - Filter by keyword: uv run pytest -n auto -k e2e
  - Single test: uv run pytest -q tests/test_e2e.py::TestXmlRpc::test_xml_rpc_standard_call -q
- Coverage:
  - Ad-hoc: uv run pytest -n auto --cov --cov-report=term-missing
  - Configured in [tool.coverage.*] with source = modernrpc/ and some omissions.

4) Running tests via nox (matrix)
- List sessions: uvx nox -l
- Run the matrix test session, selecting Python/Django via tags added in build_test_matrix():
  - Tags are of the form py<digits> and dj<digits>, e.g. py312, dj52. Sessions also tagged "tests" and sometimes "cicd-tests".
  - Examples:
    - uvx nox -s tests -t py312 -t dj52
    - uvx nox -s tests -t py310 -t dj42
- The tests session will:
  - Create a uv-managed venv for the target Python.
  - uv sync without installing Django (explicitly excluded), then install the selected Django X.Y.*.
  - Run pytest with -n auto.
- Convenience sessions:
  - Coverage: uvx nox -s tests:coverage -- term-missing (report types: term, term-missing, annotate, html, xml, json, lcov)
  - Slowest tests: uvx nox -s tests:duration
  - Benchmarks (all supported Pythons): uvx nox -s benchmarks
  - Benchmarks (current venv only): uvx nox -s benchmarks:current-venv

5) Benchmarks
- addopts disables benchmarks by default. To run them in your current environment:
  - uv run pytest tests/benchmarks --benchmark-enable
- Note: Do not use xdist parallelization with benchmarks. The nox sessions already separate them.

6) Linting, formatting, and typing
- Ruff (lint + format) [tool.ruff]
  - Check: uv run ruff check .
  - Auto-fix: uv run ruff check . --fix
  - Format: uv run ruff format .
  - Policy highlights: line-length = 120; extensive rule set enabled (e.g., flake8-pytest-style PT, flake8-django DJ). Per-file ignores relax Bandit (S) in tests/.
- Type checking (mypy):
  - Recommended: uvx nox -s mypy (installs [dependency-groups.type-checking] into a uv venv and runs mypy)
  - Note: tests/ and docs/ are excluded from mypy checks by config.

7) Django test project and fixtures
- The pytest-django settings point at tests.project.settings. SQLite in-memory DB, minimal INSTALLED_APPS, and URL routes under tests/project/urls.py:
  - /rpc -> RpcServer.view (sync)
  - /async_rpc -> RpcServer.async_view (async)
- Namespace and procedures used by e2e tests live in tests/project/rpc.py (e.g., math.add, math.divide).
- Helpful fixtures in tests/conftest.py:
  - live_server (from pytest-django): used to make HTTP calls to the test server.
  - all_*_serializers / all_*_deserializers: parametrizes settings.MODERNRPC_* to exercise all serializer/deserializer backends.
  - rf-based request factories: xmlrpc_rf, jsonrpc_rf, jsonrpc_batch_rf to produce POST requests with prebuilt payloads.

8) Common pitfalls and tips specific to this repo
- Serializer/deserializer selection is driven by settings.MODERNRPC_*; tests that rely on live_server may be parametrized using all_* fixtures to validate all backends. If you add tests involving RPC payloads, prefer the provided request factories and helpers to ensure payload correctness.
- Async tests are supported (asyncio_mode=auto). When testing async RPC, use the /async_rpc endpoint. Ensure requests to async endpoints are awaited properly if using httpx/async clients; current suite uses requests for sync and pytest’s live_server.
- Parallelization is on by default (-n auto). Tests that are not parallel-safe should explicitly disable xdist via -n 0 locally when needed.
- For matrix testing of different Django versions, use nox rather than manually pip/uv installing alternate Django versions.

9) Building and docs
- Build wheel/sdist: uv build (artifacts placed under dist/).
- Docs:
  - Build: uvx nox -s docs:build (outputs to dist/docs)
  - Live-reload serve: uvx nox -s docs:serve (http://localhost:8001)
  - Clean: uvx nox -s docs:clean

This document intentionally focuses on project-specific details (uv/nox integration, pytest-django setup, serializers/deserializers fixtures, matrix strategy) to accelerate onboarding and reduce friction for contributors.
