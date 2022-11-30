Setup environment
=================

Since 1.0, django-modern-rpc uses ``poetry`` as main tool to manage project dependencies, environments and packaging.
It must be installed globally on your system.

Install poetry
--------------

There is multiple way to install ``poetry``. Refer to `official documentation`_ and choose your preferred method.
If you already use pipx, it can be installed very quickly.

.. _official documentation: https://python-poetry.org/docs/#installation

.. code-block:: bash

   $ pipx install poetry

Alternatively, you can use the official `get-poetry.py` install script.

.. code-block:: bash

   $ curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

.. note::
   There is plenty of solution to install poetry. Feel free to read the
   `documentation <https://python-poetry.org/docs/#installation>`_ to choose your preferred one.

Install dependencies
--------------------

Dependencies are configured in ``pyproject.toml`` file. Poetry will resolve versions and store the result into
``poetry.lock`` file, which is versioned in git repository. This help to ensure all developers have the exact same
environment (including direct and indirect dependencies versions).

.. code-block:: bash

   $ poetry install

.. note::
   This command will automatically create a new environment if needed. You do not need to create it manually.

Run tests
---------

The project have a lot of unit and functional tests to avoid regressions across new releases. They are automatically
run on CI/CD platform (currently `GitHub Actions <https://github.com/alorence/django-modern-rpc/actions>`_) on each push,
pull request and before every release.

But you should run tests on you development machine before submitting a new pull request.

Default interpreter
^^^^^^^^^^^^^^^^^^^

To run test with your current python interpreter, simply run ``pytest`` inside poetry environment.

.. code-block:: bash

   poetry run pytest

Python / Django versions matrix
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To test all python / django version combinations, you can run ``tox`` which itself run ``pytest`` in different
virtual environments with correct versions installed.

.. code-block:: shell

   $ poetry run tox

To speedup tests run, you can use ``-p`` option to parallelize environment specific tests

.. code-block:: shell

   $ poetry run tox -p 4

.. caution::

  Don't run too much parallel threads or you may slow down or completely freeze your machine !

Build docs
----------

If you need to update documentation, you can rebuild it with a simple ``make`` command (always inside ``poetry``
environment).

.. code-block:: bash
   :caption: from docs/ directory

   poetry run make html

The built files are stored inside ``dist/docs`` folder.

To simplify the process, you can run ``autobuild`` which automatically watch changes on files, rebuild docs and enable
LiveServer on compatible browsers

.. code-block:: bash
   :caption: from docs/ directory

   poetry run make serve

Code quality
------------

The project uses linting and formatting tools to unify source code definition and remove most of the typo and typing
issues. You can run any tool directly inside poetry environment, or run them directly using tox (to unify command lines
options used).

.. code-block:: bash

   poetry run tox -e black,pylint,mypy,pylama

.. important::

   These tools are run on `GitHub Actions <https://github.com/alorence/django-modern-rpc/actions>`_ and will break the
   build on errors. Don't forget to run the before submitting a pull request.
