Setup environment
=================

Since 1.0, django-modern-rpc uses ``poetry`` as main tool to manage project dependencies, environments and packaging.
It must be installed globally on your system.

Install poetry
--------------

There is multiple way to install ``poetry``. Refer to `official documentation`_ and choose your preferred method.

.. _official documentation: https://python-poetry.org/docs/#installation

If you already use pipx, installation is very quick and clean.

.. code-block:: bash

   $ pipx install poetry

Alternatively, you can use the official `get-poetry.py` install script.

.. code-block:: bash

   $ curl -sSL https://install.python-poetry.org | python3 -

Install dependencies
--------------------

Dependencies are configured in ``pyproject.toml`` file. In addition, ``poetry.lock`` file contains resolved dependency
tree. To install basic development environment, simply run

.. code-block:: bash

   $ poetry install

.. note::
   This command will automatically create a new environment if needed. You do not need to create it manually.

This will install everything needed to develop and test the library. In addition, optional group may be specified
to enable other toolset (See below)

Run tests
---------

The project have a lot of unit and functional tests to avoid regressions across new releases. They are automatically
run on CI/CD platform (currently `GitHub Actions <https://github.com/alorence/django-modern-rpc/actions>`_) on each
push, pull request and before every release.

But you should run tests on you development machine before submitting a new pull request.

System interpreter
^^^^^^^^^^^^^^^^^^

To run test with your current python interpreter, simply run ``pytest`` inside poetry environment.

.. code-block:: bash

   poetry run pytest

Python / Django versions matrix
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have multiple python versions on your system, or if you have pyenv installed, you can setup tox and perform
tests against multiple python / django versions

.. code-block:: shell

   $ poetry install --with tox
   $ pyenv local system 3.11 3.10 3.9 3.8
   $ poetry run tox

To speedup tests run, you can use ``-p`` option to parallelize environment specific tests

.. code-block:: shell

   $ poetry run tox -p 4

.. caution::

  Don't run too much parallel threads or you may slow down or completely freeze your machine !

Build docs
----------

If you need to update documentation, first install required dependencies

.. code-block:: bash

   poetry install --with docs

Then, `cd` into docs directory and use Makefile pre-defined commands.

To build docs with required options:

.. code-block:: bash
   :caption: from docs/ directory

   poetry run make html

The built files are stored inside ``dist/docs`` folder.

To simplify the writing process, you can run ``autobuild`` which automatically watch
changes on files, rebuild docs and enable LiveServer on compatible browsers

.. code-block:: bash
   :caption: from docs/ directory

   poetry run make serve

Code quality
------------

The project uses linting and formatting tools to unify source code definition and remove most of the typo and typing
issues. You can run any tool directly inside poetry environment, or run them directly using tox (to unify command lines
options used).

.. code-block:: bash

   poetry install --with code-analysis
   poetry run tox -e mypy,ruff

.. important::

   These tools are run on `GitHub Actions <https://github.com/alorence/django-modern-rpc/actions>`_ and will break the
   build on errors. Don't forget to run the before submitting a pull request.
