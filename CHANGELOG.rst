Changelog
=========

Release 0.8.0 (2017-07-12)
--------------------------
- Fixed invalid HTML tag rendered from RPC Method documentation. Single new lines are converted to space since they
  are mostly used to limit docstrings line width. See pull request #7, thanks to @adamdonahue
- Fixed issue #8: signature of ``auth.set_authentication_predicate`` has been fixed so it can be used as decorator_.
  Thanks to @aplicacionamedida

.. _decorator: http://django-modern-rpc.readthedocs.io/en/latest/advanced/authentication.html#basics

Release 0.7.1 (2017-06-24)
--------------------------
- Removed useless settings variable introduced in last 0.7.0 release. Logging capabilities are now enabled by simply
  configuring a logger for ``modernrpc.*`` modules, using Django variable ``LOGGING``. The documentation_ has been
  updated accordingly.

Release 0.7.0 (2017-06-24)
--------------------------
- Default logging behavior has been changed. The library will not output any log anymore, unless
  ``MODERNRPC_ENABLE_LOGGING`` is set to True. See documentation_ for more information

.. _documentation: http://django-modern-rpc.readthedocs.io/en/latest/advanced/tips_and_tricks.html#enable-logging

Release 0.6.0 (2017-05-13)
--------------------------
- Many performance improvements. The Django cache system was previously used to store the list of available methods
  in the current project. This was mostly useless, and caused issues with some cache systems (#5). Use of cache system
  has been completely removed. The list of RPC methods is computed when the application is started and kept in memory
  until it is stopped.

Release 0.5.2 (2017-04-18)
--------------------------
- User instance is now correctly stored in the current request after successful authentication [#4]
- Unit testing with Django 1.11 is now performed against release version (Beta and RC are not tested anymore)
- Documentation has been improved

Release 0.5.1 (2017-03-25)
--------------------------
- When RPC methods are registered, if a module file contains errors, a python warning is produced. This ensure the
  message will be displayed even if the logging system is not configured in a project (#2)
- Python 2 strings standardization. Allow to configure an automatic conversion of incoming strings, to ensure they have
  the same type in RPC method, no matter what protocol was used to call it. Previously, due to different behavior
  between JSON and XML deserializers, strings were received as ``str`` when method was called via XML-RPC and as
  ``unicode`` with JSON-RPC. This standardization process is disabled by default, and can be configured for the whole
  project or for specific RPC methods.
- Tests are performed against Django 1.11rc1
- ``modernrpc.core.register_method()`` function was deprecated since version 0.4.0 and has been removed.

Release 0.5.0 (2017-02-18)
--------------------------
- Typo fixes
- JSON-RPC 2.0 standard explicitly allows requests without 'params' member. This doesn't produce error anymore.
- Setting variable ``MODERNRPC_XML_USE_BUILTIN_TYPES`` is now deprecated in favor of
  ``MODERNRPC_XMLRPC_USE_BUILTIN_TYPES``
- Unit tests are now performed with python 3.6 and Django 1.11 alpha, in addition to supported environment already
  tested. This is a first step to full support for these environments.
- HTTP "Basic Auth" support: it is now possible to define RPC methods available only to specific users. The control can
  be done on various user attributes: group, permission, superuser status, etc.
  Authentication backend can be extended to support any method based on incoming request.

Release 0.4.2 (2016-11-20)
--------------------------
- Various performance improvements
- Better use of logging framework (python builtin) to report errors & exceptions from library and RPC methods
- Rewritten docstring parser. Markdown and reStructured formatters are still supported to generate HTML documentation
  for RPC methods. They now have unit tests to validate their behavior.
- @rpc_method decorator can be used with or without parenthesis (and this feature is tested)
- System methods have been documented

Release 0.4.1 (2016-11-17)
--------------------------
- Method arguments documentation keep the same order as defined in docstring
- API change: ``MODERNRPC_ENTRY_POINTS_MODULES`` setting have been renamed to ``MODERNRPC_METHODS_MODULES``.
- A simple warning is displayed when ``MODERNRPC_METHODS_MODULES`` is not set, instead of a radical
  ``ImproperlyConfigured`` exception.
- Some traces have been added to allow debugging in the module easily. It uses the builtin logging framework.

Release 0.4.0 (2016-11-17)
--------------------------
- API change: new unified way to register methods. Documentation in progress
- API change: XMl-RPC handler will now correctly handle None values by default. This behavior can be configured using
  ``MODERNRPC_XMLRPC_ALLOW_NONE`` setting.
- Bugfix: when django use a persistent cache (Redis, memcached, etc.), ensure the registry is up-to-date
  with current sources at startup

Release 0.3.2 (2016-10-26)
--------------------------
- Include missing templates in pypi distribution packages

Release 0.3.1 (2016-10-26)
--------------------------
- HTML documentation automatically generated for an entry point
- 'system.multicall' is now supported, only in XML-RPC
- Many tests added

Release 0.3.0 (2016-10-18)
--------------------------
- Settings variables have been renamed to limit conflicts with other libraries. In the future, all settings will have
  the same prefix.

  * ``JSONRPC_DEFAULT_DECODER`` becomes ``MODERNRPC_JSON_DECODER``
  * ``JSONRPC_DEFAULT_ENCODER`` becomes ``MODERNRPC_JSON_ENCODER``

  See https:/alorence/django-modern-rpc/blob/master/modernrpc/config.py for more details
- Many other settings added, to make the library more configurable. See
  http://django-modern-rpc.readthedocs.io/en/latest/basic_usage/settings.html
- RPC methods can now declare the special ``**kwargs`` parameter. The dict will contain information about current
  context (request, entry point, protocol, etc.)
- About 12 tests added to increase coverage
- Many documentation improvements
- 'system.methodHelp' is now supported

Release 0.2.3 (2016-10-13)
--------------------------
- Useless tests & testsite packages have been removed from Pypi distributions (binary & source)

Release 0.2.2 (2016-10-13)
--------------------------
- Useless tests packages have been removed from Pypi distributions (binary & source)

Release 0.2.1 (2016-10-12)
--------------------------
- Project is now configured to report tests coverage. See https://coveralls.io/github/alorence/django-modern-rpc
- Some documentation have been added, to cover more features of the library.
  See http://django-modern-rpc.readthedocs.io/en/latest/
- Many unit tests added to increase coverage
- ``RPCEntryPoint`` class can now be configured to handle only requests from a specific protocol

Release 0.2.0 (2016-10-05)
--------------------------
- Added very basic documentation: http://django-modern-rpc.rtfd.io/
- 'system.listMethods' is now supported
- 'system.methodSignature' is now supported
- Error reporting has been improved. Correct error codes and messages are returned on usual fail cause.
  See module modernrpc.exceptions for more information.
- Many unit tests have been added to increase test coverage of the library

Release 0.1.0 (2016-10-02)
--------------------------
- First version with very basic features:

  * Works with Python 2.7, 3.3, 3.4 (Django 1.8 only) and 3.5
  * Works with Django 1.8, 1.9 and 1.10
  * Supports JSON-RPC and XML-RPC simple requests
  * Supports multiple entry-points with defined list of methods and
    supported protocols
- Some important features are still **missing**:

  * No authentication support
  * Unit tests doesn't cover all the code
  * RPC system methods utility (listMethods, methodSignature, etc.)
    are not implemented
  * There is no way to provide documentation in HTML form
  * The library itself doesn't have any documentation (appart from
    README.md)
