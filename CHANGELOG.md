# Changelog

## v1.0.1

**Release date: 2023-01-26**

### Fixes

  - Fixed invalid argument used to initialized default handlers instances (#52). Thanks to @washeck

## v1.0.0

**Release date: 2023-01-03**

After months of work, the 1.0 milestone is a major refactoring of the library. Many parts of the project have been
modernized to improve readability and robustness, and a few issues were fixed.

### Improvements
  - Type hinting is now supported in RPC methods. Auto-generated documentation will use it when it is defined.
  Old-style "doctypes" are still supported.
  - Dependency to `six` have been completely removed

### Breaking Changes
  - When an authentication error is raised, the returned status code is now 200 instead of 403 for consistency with
  batch and system.multicall requests (#35)
  - Django < 2.1 and Python < 3.5 support have been dropped.

### Other API changes
  - A new `modernrpc.core.Protocol` enum has been introduced to enforce correct protocol value when needed. (#29, #30).
  This new class replaces `modernrpc.core.JSONRPC_PROTOCOL` and `modernrpc.core.XMLRPC_PROTOCOL` but aliases were
  created for backward compatibility.
  - `RPCUnknownMethod` exception has been renamed to `RPCMethodNotFound`. An alias has been created
  for backward compatibility

### Fixes
  - Initialization process updated: exceptions are now raised on startup for invalid RPC modules. In addition, Django
  check system is used to notify common errors. This was requested multiple times (#2, #13, #34).
  - JSON-RPC notification behavior has been fixed to respect standard. Requests without `id` are handled as
  notifications but requests with null `id` are considered invalid and will return an error
  - Batch request behavior has been fixed when one or more results failed to be serialized
  - Builtin `system.methodSignature` behavior have been updated to respect standard. It now returns a list of
  list and unknown types are returned as "undef" (see http://xmlrpc-c.sourceforge.net/introspection.html)

### Misc
  - Added support for Python 3.9, 3.10 and 3.11
  - Added support for Django 3.2, 4.0 and 4.1
  - Documentation tree was completely reworked for clarity and simplicity. A new theme (Book) is now used to improve
  readability. See <https://django-modern-rpc.rtfd.io>.
  - Poetry is now used to configure project dependencies and build distributions. The new `pyproject.toml` file
  replaces `setup.py`, `setup.cfg`, `MANIFEST.in` and `requirements.txt` to centralize all dependencies,
  external tools settings (pytest, flake8, etc.) and packaging configuration
  - Black is now used to automatically format code
  - Mypy is now used to verify type hints consistency
  - Tox configuration now includes pylama, mypy, pylint and black environments
  - All tests have been rewritten to have a strong separation between unit and functional tests. Test classes where
  created to group tests by similarities. Many fixtures have been added, with more parameterization, resulting in
  about 350 tests executed covering more than 95% of the code.


## v0.12.1

**Release date: 2020-06-11**

### Fixes

  - Fix `ImportError` with Django 3.1

## v0.12.0

**Release date: 2019-12-05**

### Misc

  - Django 2.1, 2.2 and 3.0 are now officially supported. Thanks to @atodorov for 3.0 compatibility
  - Added Python 3.7 and 3.8 support
  - Dropped Python 3.3 support

### Improvements

  - To ensure compatibility with [JSON-RPC 1.2](https://www.jsonrpc.org/historical/json-rpc-over-http.html),
  2 more "Content-Type" values are supported by JSON-RPC Handler: "application/json-rpc" and
  "application/jsonrequest" (#24). Thanks to @dansan

## v0.11.1

**Release date: 2018-05-13**

### Improvements

Last release introduced some undocumented breaking API changes regarding RPC registry management. Old API has been
restored for backward compatibility. The following global functions are now back in the API:

  - modernrpc.core.register\_rpc\_method()
  - modernrpc.core.get\_all\_method\_names()
  - modernrpc.core.get\_all\_methods()
  - modernrpc.core.get\_method()
  - modernrpc.core.reset\_registry()

In addition, some improvements have been applied to unit tests, to make sure test environment is the same after each
test function. In addition, some exclusion patterns have been added in .coveragerc file to increase coverage
report accuracy.

## v0.11.0

**Release date: 2018-04-25**

### Improvements

  - Django 2.0 is now officially supported. Tox and Travis default config have been updated to integrate Django 2.0 in
  existing tests environments.
  - Method's documentation is generated only if needed and uses Django's @cached\_property decorator
  - HTML documentation default template has been updated: Bootstrap 4.1.0 stable is now used, and the rendering has
  been improved.
  - Many units tests have been improved. Some tests with many calls to LiveServer have been split into shorter ones.

### API Changes

  - Class RPCRequest has been removed and replaced by method `execute_procedure(name, args, kwargs)` in `RPCHandler`
  class. This method contains common logic used to retrieve an RPC method, execute authentication predicates to make
  sure it can be run, execute the concrete method and return the result.
  - HTML documentation content is not marked as "safe" anymore, using `django.utils.safestring.mark_safe()`. You have to
  use Django decorator `safe` in your template if you display this value.

### Settings

  - The `kwargs` dict passed to RPC methods can have customized keys (#18). Set the following values:
    - `settings.MODERNRPC_KWARGS_REQUEST_KEY`
    - `settings.MODERNRPC_KWARGS_ENTRY_POINT_KEY`
    - `settings.MODERNRPC_KWARGS_PROTOCOL_KEY`
    - `settings.MODERNRPC_KWARGS_HANDLER_KEY`

to override dict keys and prevent conflicts with your own methods arguments.


## v0.10.0

**Release date: 2017-12-06**

### Improvements

  - Logging system / error management
    - In case of error, current exception stacktrace is now passed to logger by default. This allows special handler
      like `django.utils.log.AdminEmailHandler` or `raven.handlers.logging.SentryHandler` to use it to report more
      useful information (#13)
    - Error messages have been rewritten to be consistent across all modules and classes
    - Decrease log verbosity: some `INFO` log messages now have `DEBUG` level (startup methods registration)
  - Documentation has been updated
    - Added a page to explain how to configure RPC methods documentation generation, and add a note to explicitly state
      that `markdown` or `docutils` package must be installed if `settings.MODERNRPC_DOC_FORMAT` is set to non-empty
      value (#16)
    - Added a page to list implemented system introspection methods
    - Added a bibliography page, to list all references used to write the library
  - Default template for generated RPC methods documentation now uses Bootstrap 4.0.0-beta.2 (previously 4.0.0-alpha.5)

## v0.9.0

**Release date: 2017-10-03**

This is a major release with many improvements, protocol support and bug fixes. This version introduces an API break,
please read carefully.

### Improvements

  - Class `RPCException` and its subclasses now accept an additional `data` argument (#10). This is used by JSON-RPC
  handler to report additional information to user in case of error. This data is ignored by XML-RPC handler.
  - JSON-RPC: Batch requests are now supported (#11)
  - JSON-RPC: Named parameters are now supported (#12)
  - JSON-RPC: Notification calls are now supported. Missing "id" in a payload is no longer considered as invalid, but is
  correctly handled. No HTTP response is returned in such case, according to the standard.
  - XML-RPC: exception raised when serializing data to XML are now caught as `InternalError` and a clear error message

### API Changes

  - Both `modernrpc.handlers.JSONRPC` and `modernrpc.handlers.XMLRPC` constants were moved and renamed. They become
  respectively `modernrpc.core.JSONRPC_PROTOCOL` and `modernrpc.core.XMLRPC_PROTOCOL`
  - `RPCHandler` class updated, as well as subclasses `XMLRPCHandler` and `JSONRPCHandler`. `RPCHandler.parse_request()`
  is now `RPCHandler.process_request()`. The new method does not return a tuple `(method_name, params)` anymore.
  Instead, it executes the underlying RPC method using new class `RPCRequest`. If you customized your handlers, please
  make sure you updated your code (if needed).

### Fixes

  - Code has been improved to prepare future compatibility with Django 2.0

## v0.8.1

**Release date: 2017-10-02**

> **important**
>
> This version is a security fix. Upgrade is highly recommended

### Security fix

  - Authentication backend is correctly checked when executing method using `system.multicall()`

## v0.8.0

**Release date: 2017-07-12**

### Fixes

  - Fixed invalid HTML tag rendered from RPC Method documentation. Single new lines are converted to space since they are
  mostly used to limit docstrings line width. See pull request #7, thanks to @adamdonahue
  - Signature of `auth.set_authentication_predicate` has been fixed. It can now be used as decorator (#8). See the
  [documentation](https://django-modern-rpc.rtfd.io//en/latest/docs/authentication.html) for details.
  Thanks to @aplicacionamedida

## v0.7.1

**Release date: 2017-06-24**

### Fixes

  - Removed useless settings variable introduced in last 0.7.0 release. Logging capabilities are now enabled by simply
  configuring a logger for `modernrpc.*` modules, using Django variable `LOGGING`. The
  [documentation](https://django-modern-rpc.rtfd.io/en/latest/docs/error_handling.html) has been updated accordingly.

## v0.7.0

**Release date: 2017-06-24**

### Improvements

  - Default logging behavior has changed. The library will not output any log anymore, unless `MODERNRPC_ENABLE_LOGGING`
  is set to True. See [docs](https://django-modern-rpc.rtfd.io/en/latest/docs/error_handling.html) for details

## v0.6.0

**Release date: 2017-05-13**

### Improvements

  - Django cache system was previously used to store the list of available methods in the current project.
  This was useless, and caused issues with some cache systems (#5). Use of cache system has been removed. The list of
  RPC methods is computed when the application is started and kept in memory until it is stopped.

## v0.5.2

**Release date: 2017-04-18**

### Improvements

  - HTTP Basic Authentication backend: User instance is now correctly stored in current request after successful
  authentication (#4)
  - Unit testing with Django 1.11 is now performed against release version (Beta and RC are not tested anymore)
  - Various Documentation improvements

## v0.5.1

**Release date: 2017-03-25**

### Improvements

  - When RPC methods are registered, if a module file contains errors, a python warning is produced. This ensures the
  message will be displayed even if the logging system is not configured in a project (#2)
  - Python 2 strings standardization. Allow to configure an automatic conversion of incoming strings, to ensure they have
  the same type in RPC method, no matter what protocol was used to call it. Previously, due to different behavior
  between JSON and XML deserializers, strings were received as `str` when method was called via XML-RPC and as `unicode`
  with JSON-RPC. This standardization process is disabled by default, and can be configured for the whole project or for
  specific RPC methods.
  - Tests are performed against Django 1.11rc1
  - `modernrpc.core.register_method()` function was deprecated since version 0.4.0 and has been removed.

## v0.5.0

**Release date: 2017-02-18**

### Improvements

  - Typo fixes
  - JSON-RPC 2.0 standard explicitly allows requests without 'params' member. This doesn't produce error anymore.
  - Setting variable `MODERNRPC_XML_USE_BUILTIN_TYPES` is now deprecated in favor of `MODERNRPC_XMLRPC_USE_BUILTIN_TYPES`
  - Unit tests are now performed with python 3.6 and Django 1.11 alpha, in addition to supported environment already
  tested. This is a first step to full support for these environments.
  - HTTP "Basic Auth" support: it is now possible to define RPC methods available only to specific users. The control can
  be done on various user attributes: group, permission, superuser status, etc. Authentication backend can be extended
  to support any method based on incoming request.

## v0.4.2

**Release date: 2016-11-20**

### Improvements

  - Various performance improvements
  - Better use of logging system (python builtin) to report errors & exceptions from library and RPC methods
  - Rewritten docstring parser. Markdown and reStructured formatters are still supported to generate HTML documentation
  for RPC methods. They now have unit tests to validate their behavior.
  - @rpc_method decorator can be used with or without the parenthesis (and this feature is tested)
  - System methods have been documented

## v0.4.1

**Release date: 2016-11-17**

### Improvements

  - Method arguments documentation keep the same order as defined in docstring
  - API change: `MODERNRPC_ENTRY_POINTS_MODULES` setting have been renamed to `MODERNRPC_METHODS_MODULES`.
  - A simple warning is displayed when `MODERNRPC_METHODS_MODULES` is not set, instead of a radical `ImproperlyConfigured`
  exception.
  - Some traces have been added to allow debugging in the module easily. It uses the builtin logging framework.

## v0.4.0

**Release date: 2016-11-17**

### API Changes

  - New unified way to register methods. Documentation in progress
  - XMl-RPC handler will now correctly serialize and unserialize None values by default. This behavior can be configured
  using `MODERNRPC_XMLRPC_ALLOW_NONE` setting.

### Fixes

  - When django use a persistent cache (Redis, memcached, etc.), ensure the registry is up-to-date with current sources
  at startup

## v0.3.2

**Release date: 2016-10-26**

### Fixes

  - Include missing templates in pypi distribution packages

## v0.3.1

**Release date: 2016-10-26**

### Improvements

  - HTML documentation automatically generated for an entry point
  - `system.multicall` is now supported, only in XML-RPC
  - Many tests added

## v0.3.0

**Release date: 2016-10-18**

### API Changes

  - Settings variables have been renamed to limit conflicts with other libraries. In the future, all settings will have
  the same prefix.

    - `JSONRPC_DEFAULT_DECODER` becomes `MODERNRPC_JSON_DECODER`
    - `JSONRPC_DEFAULT_ENCODER` becomes `MODERNRPC_JSON_ENCODER`

    See <https://github.com/alorence/django-modern-rpc/blob/master/modernrpc/conf/default_settings.py> for more details
  - Many other settings added, to make the library more configurable. See
  <https://django-modern-rpc.rtfd.io/en/latest/basic_usage/settings.html>

### Improvements

  - RPC methods can now declare the special `**kwargs` parameter. The dict will contain information about current context
  (request, entry point, protocol, etc.)
  - About 12 tests added to increase coverage
  - Many documentation improvements
  - `system.methodHelp` is now supported

## v0.2.3

**Release date: 2016-10-13**

### Fixes

  - Packages `modernrpc.tests` and `testsite` were excluded from Pypi distribution (both binary and source). This action
  was forgotten in the last release

## v0.2.2

**Release date: 2016-10-13**

### Fixes

  - Packages `modernrpc.tests` and `testsite` were excluded from Pypi distribution (both binary and source)

## v0.2.1

**Release date: 2016-10-12**

### Improvements

  - Project is now configured to report tests coverage. See <https://coveralls.io/github/alorence/django-modern-rpc>
  - Some documentation have been added, to cover more features of the library. See  <https://django-modern-rpc.rtfd.io/>
  - Many unit tests added to increase coverage
  - `RPCEntryPoint` class can now be configured to handle only requests from a specific protocol

## v0.2.0

**Release date: 2016-10-05**

### Improvements

  - Added very basic documentation: <https://django-modern-rpc.rtfd.io/>
  - `system.listMethods` is now supported
  - `system.methodSignature` is now supported
  - Error reporting has been improved. Correct error codes and messages are returned on usual fail cause. See module
  `modernrpc.exceptions` for more information.
  - Many unit tests have been added to increase test coverage of the library

## v0.1.0

**Release date: 2016-10-02**

This is the very first version of the library. Only a subset of planned features were implemented

### Current features

  - Work with Python 2.7, 3.3, 3.4 (Django 1.8 only) and 3.5
  - Work with Django 1.8, 1.9 and 1.10
  - JSON-RPC and XML-RPC simple requests support
  - Multiple entry-points with defined list of methods and supported protocols

### Not implemented yet

  - No authentication support
  - Unit tests doesn't cover all the code
  - RPC system methods utility (`listMethods`, `methodSignature`, etc.) are not yet implemented
  - There is no way to provide documentation in HTML form
  - The library itself doesn't have any documentation (apart from the README.md)
