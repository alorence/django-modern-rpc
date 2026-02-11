# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

django-modern-rpc is a Python/Django library that provides an embedded XML-RPC and JSON-RPC 2.0 server. It lets developers expose Python functions as RPC endpoints within a Django project. Key capabilities: pluggable serialization backends (orjson, rapidjson, lxml, etc.), authentication via predicates, async support, batch requests (JSON-RPC), and built-in introspection (system.listMethods, system.methodHelp, etc.).

## Common commands

### Setup
```bash
uv sync                          # Install runtime + dev + tests dependencies
```

### Tests
```bash
uv run pytest -n auto                    # Full test suite (parallelized)
uv run pytest -n auto -k "jsonrpc"       # Filter by keyword
uv run pytest tests/test_e2e.py::TestXmlRpc::test_xml_rpc_standard_call  # Single test
uv run pytest -n auto --cov --cov-report=term-missing                    # With coverage
```

### Matrix testing (Python × Django combinations via nox)
```bash
uvx nox -l                               # List available sessions
uvx nox -s tests -t py312 -t dj52        # Specific Python/Django combo
uvx nox -s tests:coverage -- term-missing # Coverage report
```

### Linting and formatting
```bash
uv run ruff check .           # Lint
uv run ruff check . --fix     # Lint with auto-fix
uv run ruff format .          # Format
uv run ruff format . --check  # Check formatting
```

### Type checking
```bash
uvx nox -s mypy    # mypy (excludes tests/ and docs/)
uvx nox -s ty      # ty (faster alternative)
```

### Benchmarks
```bash
uv run pytest tests/benchmarks --benchmark-enable   # Current venv
uvx nox -s benchmarks                               # All Python versions
```
Note: benchmarks must not use `-n auto` (no xdist parallelization).

### Documentation
```bash
uvx nox -s docs:build   # Build to dist/docs
uvx nox -s docs:serve   # Live-reload at localhost:8001
```

## Architecture

### Core flow

```
Django URL route → RpcServer → RpcHandler (JSON-RPC or XML-RPC) → ProcedureWrapper → user function
```

1. **RpcServer** (`modernrpc/server.py`) — Central orchestrator. Maintains a procedure registry, validates HTTP requests, selects the appropriate handler based on Content-Type, and exposes `.view` (sync) and `.async_view` (async) properties for Django URL routing.

2. **RegistryMixin** / **RpcNamespace** (`modernrpc/server.py`) — Shared registration logic. `RpcNamespace` groups related procedures under a dotted prefix (e.g., `math.add`). Both `RpcServer` and `RpcNamespace` inherit from `RegistryMixin`.

3. **RpcHandler** (`modernrpc/handler.py`) — Abstract base class for protocol handlers. Defines `can_handle()`, `process_request()` / `aprocess_request()`, and response builders.
   - **JsonRpcHandler** (`modernrpc/jsonrpc/handler.py`) — JSON-RPC 2.0: named params, batch requests, notifications.
   - **XmlRpcHandler** (`modernrpc/xmlrpc/handler.py`) — XML-RPC: single calls, system multicall.

4. **ProcedureWrapper** (`modernrpc/core.py`) — Wraps a callable/coroutine for RPC execution. Stores auth predicates, protocol restriction, and an optional `context_target` argument name for injecting `RpcRequestContext`.

5. **Backend system** — Pluggable serialization/deserialization per protocol:
   - JSON: `modernrpc/jsonrpc/backends/` (json, orjson, rapidjson, simplejson)
   - XML: `modernrpc/xmlrpc/backends/` (xmlrpc, lxml, etree, xmltodict)
   - Selected via `MODERNRPC_*_SERIALIZER` / `MODERNRPC_*_DESERIALIZER` Django settings.

6. **System procedures** (`modernrpc/system_procedures.py`) — Auto-registered under `system.*` namespace: `listMethods`, `methodSignature`, `methodHelp`, `multicall`.

### Exception hierarchy (`modernrpc/exceptions.py`)

`RPCException` (base) → `RPCParseError` (-32700), `RPCInvalidRequest` (-32600), `RPCMethodNotFound` (-32601), `RPCInvalidParams` (-32602), `RPCInternalError` (-32603), `AuthenticationError`, etc.

### Test infrastructure

- Django test project: `tests/project/` (settings, urls, rpc procedures)
  - `/rpc` → sync view, `/async_rpc` → async view
  - Procedures defined in `tests/project/rpc.py`
- Fixtures in `tests/conftest.py`: `all_*_serializers` / `all_*_deserializers` parametrize backends; `xmlrpc_rf`, `jsonrpc_rf`, `jsonrpc_batch_rf` build POST requests with correct payloads.
- pytest-asyncio in auto mode (session-scoped loop). Async tests use the `/async_rpc` endpoint.
- Parallelization on by default (`-n auto`). Tests that aren't parallel-safe should use `-n 0`.

## Code style

- Line length: 120 characters
- Formatter/linter: ruff (extensive rule set, see `pyproject.toml [tool.ruff.lint]`)
- Bandit (S) rules disabled in `tests/`
- Double quotes, LF line endings
