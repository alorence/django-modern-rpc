Home
====

RPC (Remote Procedure Call) is a network protocol used to call functions on another system or web server
through HTTP POST requests. It has been around for decades and is one of the predecessors of modern Web API protocols
(REST, GraphQL, etc.).

While newer alternatives exist, there are still use-cases where XML-RPC or JSON-RPC servers are needed.
**Django-modern-rpc** helps you set up such a server as part of your Django project.

Version 2.0 brings significant improvements to the library, including a more intuitive API, better error handling,
improved type annotations, and more flexible configuration options.

.. image:: https://img.shields.io/pypi/l/django-modern-rpc?style=for-the-badge
   :alt: PyPI - License

.. image:: https://img.shields.io/github/issues-raw/alorence/django-modern-rpc?style=for-the-badge
   :alt: GitHub issues
   :target: https://github.com/alorence/django-modern-rpc/issues

.. image:: https://img.shields.io/pypi/v/django-modern-rpc?style=for-the-badge
   :alt: PyPI
   :target: https://pypi.org/project/django-modern-rpc/

.. image:: https://img.shields.io/github/release-date/alorence/django-modern-rpc?style=for-the-badge
   :alt: GitHub Release Date
   :target: https://github.com/alorence/django-modern-rpc/releases

Getting started
---------------

.. important:: django-modern-rpc requires python 3.8+ and Django 3.2+. If you need to install it in environment with
   older Python/Django versions, you must install a previous release. See :ref:`Changelog` for more information.

Installing the library and configuring a Django project to use it can be achieved in a few minutes. Follow
:doc:`quickstart` for very basic setup process. Later, when you will need to configure more precisely
your project, follow other topics in the menu.

.. toctree::
   :hidden:

   quickstart.rst
   server.rst
   procedure_registration.rst
   backends.rst
   authentication.rst
   error_handling.rst
   security.rst
   faq.rst
   references.rst
   migration_guide.rst

.. toctree::
   :caption: Miscellaneous
   :name: misc
   :hidden:

   changelog.rst
   contribute/contribute.rst
   contribute/setup_environment.rst
