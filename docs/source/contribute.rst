============
Get involved
============

There is many way to contribute to project development.

Report issues, suggest enhancements
===================================

If you find a bug, want to ask question about configuration or suggest an improvemnt to the project, feel free to use
`the issue tracker <https://github.com/alorence/django-modern-rpc/issues>`_. You will need a GitHub account.

Submit a pull request
=====================

If you improved something or fixed a bug by yourself in a fork, you can
`submit a pull request <https://github.com/alorence/django-modern-rpc/pulls>`_. We will be happy to review it before
doing the merge.

Execute the unit tests
======================

The project uses py.test with some plugins to perform unit testing. You can install most of them using ``pip``.
In addition, you will have to install a supported version of Django. This is not part of ``requirements.txt`` since the
automatic tests are performed on various Django versions. To install all dependencies for unit tests execution, you
can type::

   pip install Django
   pip install -r requirements.txt

The file ``requirements.txt`` contains references to the following packages:

.. literalinclude:: ../../requirements.txt

Installing ``pytest-django`` will trigger ``pytest`` and all its dependencies. In addition, ``requests`` is used to
simulate JSON-RPC calls in tests. In the future, a proper JSON-RPC library may be used.

When all required packages are installed, you can run the tests using::

   pytest .

Execute unit tests in all supported environments
================================================

Alternatively to simple ``pytest`` run, you may want to check if the tests run correctly in all supported configuration.
To do so, you can install and run ``tox``::

   pip install tox
   tox .

This will execute all tests under all supported Python and Django versions. Also, it will execute ``flake8`` to perform
code style checks.