Home
====

RPC (Remote Procedure Call) is a pretty old network protocol used to call functions on another system or web server
through HTTP POST requests. It has been created decades ago and is one of the predecessor of modern Web API protocols
(REST, GraphQL, etc.).

While it is a bit outdated now, there is still use-cases were XML-RPC or JSON-RPC server must be implemented. This
library will help you setup such a server as part of your Django project.

Getting started
---------------

.. important:: This library requires python 3.5 and Django 2.1. If you need to install it on older Python/Django
   versions, you may need to install an older release.

Installing the library and configuring a Django project can be done in a few minutes. Follow :doc:`basics/quickstart`
for very basic setup process. Later, when you will need to configure more precisely your project, follow other topics
in the menu.

Useful links
------------


:Sources:   https://github.com/alorence/django-modern-rpc
:Issues:    https://github.com/alorence/django-modern-rpc/issues
:Package:   https://pypi.org/project/django-modern-rpc/
:License:   MIT

Changelog
---------

.. include:: ../CHANGELOG.md
   :parser: myst_parser.sphinx_
   :start-line: 1


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

.. toctree::
   :caption: How to contribute
   :name: contribute
   :hidden:

   contribute/contribute.rst
   contribute/setup_environment.rst
