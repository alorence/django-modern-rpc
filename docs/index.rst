Home
====

:abbr:`RPC (Remote Procedure Call)` is a network protocol used to call functions on another system or web server
through HTTP POST requests. It has been around for decades and is one of the predecessors of modern Web API protocols
(REST, GraphQL, etc.).

While newer alternatives exist, there are still use-cases where XML-RPC or JSON-RPC servers are needed.
**Django-modern-rpc** helps you set up such a server as part of your Django project. It provide a simple and pythonic
API to expose global functions to be called from other websites or programs.

Version 2.0 brings significant improvements to the library, including a more intuitive API, better error handling,
reworked authentication system, improved type annotations, and more flexible configuration options.

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

.. important:: django-modern-rpc requires Python 3.10+ and Django 4.2+. If you need to install it in environment with
   older Python / Django versions, you must install a previous release. See :ref:`Changelog` for more information.

Installing the library and configuring a Django project to use it can be achieved in a few minutes. Follow
:doc:`quickstart` for very basic setup process. Later, when you will need to configure more precisely
your project, follow other topics in the menu.

.. toctree::
   :hidden:

   quickstart.rst

.. toctree::
   :caption: Configuration
   :name: config
   :maxdepth: 2

   config/server.rst
   config/procedure_registration.rst
   config/authentication.rst
   config/error_handling.rst
   config/backends.rst
   config/generated_doc.rst
   config/settings

.. toctree::
   :caption: Miscellaneous
   :name: misc
   :maxdepth: 2

   misc/security.rst
   misc/faq.rst
   misc/migration_guide.rst
   misc/contributing.rst
   misc/proto_refs.rst
   misc/changelog.rst
