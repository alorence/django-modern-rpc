Changelog
=========

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
