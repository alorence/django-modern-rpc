from modernrpc.views import RPCEntryPoint


def test_bench_error_result(benchmark, rf):
    request = rf.post("/rpc2", data="invalid_content", content_type="application/xml")
    view = RPCEntryPoint.as_view()

    res = benchmark(view, request)

    assert res.status_code == 200
    assert res.content == (
        b'<?xml version="1.0"?>\n            <methodResponse>\n                <faul'
        b"t>\n<value><struct>\n<member>\n<name>faultCode</name>\n<value><int>-32700</i"
        b"nt></value>\n</member>\n<member>\n<name>faultString</name>\n<value><string>P"
        b"arse error, unable to read the request: Error while parsing XML-RPC request:"
        b" syntax error: line 1, column 0</string></value>\n</member>\n</struct></va"
        b"lue>\n</fault>\n\n            </methodResponse>"
    )


def test_bench_success_result(benchmark, rf):
    payload = b"""<?xml version="1.0"?>
    <methodCall>
      <methodName>add</methodName>
      <params>
         <param>
            <value><int>95</int></value>
         </param>
         <param>
            <value><int>222</int></value>
         </param>
      </params>
    </methodCall>"""

    request = rf.post("/rpc2", data=payload, content_type="application/xml")
    view = RPCEntryPoint.as_view()

    res = benchmark(view, request)

    assert res.status_code == 200
    assert b"not well-formed (invalid token)" not in res.content
    assert b"<value><int>317</int></value>" in res.content
