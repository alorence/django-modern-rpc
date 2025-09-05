Contribution guide
===================

Introduction
------------

django-modern-rpc is an open-source project maintained by a single developer on his free time. Any contribution
is welcome!

If you find an issue or want to ask for a new feature, open a new ticket on the project's issue tracker:
https://github.com/alorence/django-modern-rpc/issues

If you want to solve an existing issue or implement a new feature, you can fork the project, push your changes and
open a pull request: https://github.com/alorence/django-modern-rpc/pulls

Before submitting, ensure:

- Tests pass locally (at least with your prefered python version, preferably with all supported version.
  See :ref:`Matrix testing`).
- Linting and formatting are applied (Ruff), and mypy passes for supported code paths. See :ref:`Linting, formatting`
  and :ref:`Type checking`
- Documentation is updated according to your changes. See :ref:`Documentation`

This section explain everything you need to know to setup the project locally, run tests, linter, formatter, type
checker and build documentation

Local environment
^^^^^^^^^^^^^^^^^

.. _uv: https://docs.astral.sh/uv/

This project and its dependencies is managed with uv_. This is the only tool needed to start hacking into the project.
Uv can be used on any operating system to install a supported python version, create a virtual environment, install
dependencies and run `nox` (see :ref:`Optional tool`)

See https://docs.astral.sh/uv/getting-started/installation/ for detailed installation docs

Minimal setup
^^^^^^^^^^^^^

Setting up a basic local environment is very quick. Simply run:

.. code-block:: bash

   uv sync

This will install project's requirements and everything you need to run tests (i.e: dependencies from groups
``dev`` and ``tests`` are always installed).

Optional tool
^^^^^^^^^^^^^

.. _Nox: https://github.com/wntrblm/nox

Nox_ is used as a task manager to:

- Run tests against multiple combinations of Python / Django versions
- Run pre-defined commands to simplify some usual tasks (like a Makefile, but cross-platform)

You can install it globally on your system:

.. code-block:: bash

   uv tool install nox
   nox -l

Or, you can run it directly using uvx (installed with uv):

.. code-block:: bash

   uvx nox -l

In this document, we will assume ``nox`` is installed globally, but it will work either when used through ``uvx``.


Running tests
-------------

Current environment
^^^^^^^^^^^^^^^^^^^

.. _pytest: https://docs.pytest.org/en/stable/

Project's tests uses pytest_. In the local environment (default python version), run it with one of the following
commands:

.. code-block:: bash

   # Run pytest with default arguments
   uv run pytest

   # To speedup tests execution, you can use pytest-xdist plugin to parallelize on multiple cores
   uv run pytest -n auto

   # Run only a few tests, filtering by keyword
   uv run pytest -k xmlrpc

   # Run a specific test
   uv run pytest -q tests/test_e2e.py::TestXmlRpc::test_xml_rpc_standard_call

   # Display duration of 20 slowest tests
   uv run pytest --durations=20

Alternatively, use ``nox``:

.. code-block:: bash

   # Run pytest with default arguments (with parallelization)
   nox -s tests:current-venv

   # Customize pytest args
   nox -s tests:current-venv -- -k multicall

Matrix testing
^^^^^^^^^^^^^^

Use ``nox`` to run tests across multiple Python and Django versions supported by the project. Nox will use uv to
automatically install the right python version when missing.

.. code-block:: bash

   # Run all supported Python / Django versions combinations
   nox

   # Run tests suits with Python 3.12 (using tag)
   nox -t py312

   # Run tests suites with Django 5.2 (using tag)
   nox -t dj52

   # Run a specific test suite
   nox -s 'tests(Python 3.14 × Django 5.1)'

   # Run a specific test in all supported test suites (a.k.a pass command arguments to pytest)
   nox -- -k jsonrpc

.. note:: ``noxfile.py`` define tags in the form ``py<digits>`` and ``dj<digits>``, e.g. ``py312``
   for Python 3.12 and ``dj52`` for Django 5.2


Tests tips and pitfalls
^^^^^^^^^^^^^^^^^^^^^^^

- The test project used by pytest‑django lives under ``tests/project`` and exposes two routes:
  ``/rpc`` (sync) and ``/async_rpc`` (async). End‑to‑end tests use these.
- Serializer/deserializer backends are driven by settings in ``tests.project.settings`` and
  parametrized by fixtures such as ``all_*_serializers`` and ``all_*_deserializers``.
- Async tests are supported and automatically detected (``asyncio_mode=auto``).
- Parallelization is enabled by default. Disable with ``-n 0`` for tests that are not parallel‑safe.

Tests coverage
--------------

.. _pytest-cov: https://pytest-cov.readthedocs.io
.. _coverage: https://coverage.readthedocs.io

pytest-cov_ and coverage_ are used to compute code coverage analytics. To get it use:

.. code-block:: bash

   # Basic coverage (default options)
   uv run pytest --cov

   # Custom output type (see https://pytest-cov.readthedocs.io/en/latest/reporting.html#reporting)
   uv run pytest --cov --cov-report term-missing

Alternatively, use ``nox``:

.. code-block:: bash

   # Basic coverage (default options)
   nox -s tests:coverage

   # Custom output type (see https://pytest-cov.readthedocs.io/en/latest/reporting.html#reporting)
   nox -s tests:coverage -- term-missing

Benchmarks
----------

.. _pytest-benchmark: https://pytest-benchmark.readthedocs.io

To compare the performances of various backends and compare sync and async views behaviors, pytest-benchmark_ is used.
By default, benchmarks are disabled by ``addopts`` in ``pyproject.toml``. To run them in your current environment:

.. code-block:: bash

   uv run pytest tests/benchmarks --benchmark-enable

Alternatively, use ``nox``:

.. code-block:: bash

   # Run benchmarks with all supported Python versions
   nox -s benchmarks

   # Run benchmarks with specific python version
   nox -s benchmarks -t py312

   # Display duration of 20 slowest tests
   nox -s tests:duration

.. note:: Do not use xdist when running benchmarks (``-n auto``), pytest-benchmark don't support it

Linting, formatting
-------------------

.. _Ruff: https://docs.astral.sh/ruff/

This project uses Ruff_ for linting and formatting

.. code-block:: bash

   # Linting
   uv run ruff check .

   # Linting (apply basic fixes when possible)
   uv run ruff check . --fix

   # Formatting
   uv run ruff format .

Alternatively, use ``nox``:

.. code-block:: bash

   # Run benchmarks with all supported Python versions
   nox -s lint

   # Linting (apply basic fixes when possible)
   nox -s lint:fix

   # Formatting
   nox -s format

Type checking
-------------

.. important:: The requirements to use type checker are not installed by default. Make sure you ran
   ``uv sync --group type-checking`` if you want to run it directly with ``uv run``. Nox task will do it automatically

.. _Mypy: https://mypy.readthedocs.io

This project uses Mypy_ to check type hints consistency

.. code-block:: bash

   uv run mypy .

Alternatively, use ``nox``:

.. code-block:: bash

   nox -s mypy

Documentation
-------------

.. _Sphinx: https://www.sphinx-doc.org/en/master/#user-guide

Documentation is generated with Sphinx_. The easiest way to build it is using ``nox``:

.. code-block:: bash

   nox -s docs:build

Generated files can be found into ``dist/docs``. Another task can be used to wipe this directory

.. code-block:: bash

   nox -s docs:clean

.. _sphinx-autobuild: https://github.com/sphinx-doc/sphinx-autobuild

To simplify edition of the documentation, sphinx-autobuild_ plugin is available. When used, the HTML documentation
is served through a minimal HTTP server from ``http://localhost:8001``

.. code-block:: bash

   nox -s docs:serve

.. important:: The requirements to build docs are not installed by default. Make sure you ran ``uv sync --group docs``
   if you want to use them directy with ``uv run``.
