Home
====

RPC (Remote Procedure Call) is a pretty old network protocol used to call functions on another system or web server
through HTTP POST requests. It has been created decades ago and is one of the predecessor of modern Web API protocols
(REST, GraphQL, etc.).

While it is a bit outdated now, there is still use-cases were XML-RPC or JSON-RPC server must be implemented.
**Django-modern-rpc** will help you setup such a server as part of your Django project.

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

.. important:: django-modern-rpc requires python 3.7+ and Django 2.1+. If you need to install it in environment with
   older Python/Django versions, you must install a previous release. See :ref:`Changelog` for more information.

Installing the library and configuring a Django project to use it can be achieved in a few minutes. Follow
:doc:`basics/quickstart` for very basic setup process. Later, when you will need to configure more precisely
your project, follow other topics in the menu.

.. toctree::
   :hidden:

   basics/quickstart.rst

.. toctree::
   :caption: Basics
   :name: basics
   :hidden:

   basics/register_procedure.rst
   basics/entrypoints.rst
   basics/error_handling.rst
   basics/settings.rst

.. toctree::
   :caption: Advanced
   :name: advanced
   :hidden:

   advanced/implementation_details.rst
   advanced/authentication.rst
   advanced/generated_doc.rst
   advanced/security.rst

.. toctree::
   :caption: Miscellaneous
   :name: misc
   :hidden:

   changelog.rst
   contribute/contribute.rst
   contribute/setup_environment.rst
