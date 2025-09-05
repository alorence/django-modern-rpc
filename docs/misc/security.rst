Security concerns
=================

Protection against XML vulnerabilities
--------------------------------------

Why this matters
^^^^^^^^^^^^^^^^

XML parsing is historically vulnerable to several classes of attacks such as:

- External entity expansion (XXE) leaking local files or reaching internal network resources
- Billion Laughs / quadratic blowup attacks via entity expansion causing DoS
- DTD-related exploits and network retrieval during parsing

To mitigate these risks, django-modern-rpc ships with safe defaults for all XML-RPC backends
and requires `defusedxml <https://github.com/tiran/defusedxml>`_.

Backend hardening overview
^^^^^^^^^^^^^^^^^^^^^^^^^^

All built-in XML-RPC backends are configured with protections against XXE/DoS:

- `etree` backend (``xml.etree.ElementTree``)
  - Uses ``defusedxml.ElementTree`` for parsing and serialization.
  - Forbidden constructs (DTD, entities, external references) raise defusedxml exceptions, which are translated into
  ``RPCInsecureRequest``.
  - Malformed XML raises ``RPCParseError``.

- `xmltodict` backend
  - First parses with defusedxml.ElementTree.fromstring to validate securely, then feeds the result to xmltodict.
  - ``defusedxml.DefusedXmlException`` (XXE/DTD/etc.) is mapped to ``RPCInsecureRequest``; parse errors
  to ``RPCParseError``.

- `lxml` backend
  - Uses a hardened ``lxml.etree.XMLParser`` with ``resolve_entities=False``, ``no_network=True``, ``dtd_validation=False``,
  ``load_dtd=False``, ``huge_tree=False``.
  - ``XMLSyntaxError`` is mapped to ``RPCParseError``.

What you will see on insecure input
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Requests containing dangerous XML features are rejected early with an ``RPCInsecureRequest``.
- Well-formed but invalid XML for XML-RPC is rejected with ``RPCInvalidRequest``.
- Broken XML syntax results in ``RPCParseError``.

These exceptions are caught by the server and converted into safe protocol-specific responses.

Writing custom XML backends safely
----------------------------------

If you implement a custom XML-RPC backend, follow these guidelines:

- Prefer ``defusedxml`` wrappers over the stdlib XML APIs:

.. code-block:: python

  from defusedxml import ElementTree as SafeET
  root = SafeET.fromstring(xml_bytes)  # Safe parsing: DTD, entities, external refs are forbidden

- Or, when using lxml, create a locked-down parser:

.. code-block:: python

  import lxml.etree as ET

  parser = ET.XMLParser(resolve_entities=False, no_network=True, dtd_validation=False, load_dtd=False, huge_tree=False)
  root = ET.fromstring(xml_bytes, parser)


- Convert defusedxml.DefusedXmlException and parsing errors into modernrpc exceptions (``RPCInsecureRequest``,
  ``RPCParseError``) so the server can return a safe error response.

Notes
-----

- The secure defaults apply automatically; no additional configuration is required.
- Do not disable these protections in production. They exist to reduce the attack surface of XML parsing.
