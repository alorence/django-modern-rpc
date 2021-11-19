# coding: utf-8
import pytest

from modernrpc.exceptions import RPC_INVALID_PARAMS


class TestBase:
    @pytest.mark.parametrize('term_a, term_b, expected_result', [
        (5, 12, 17),
        (0, 8, 8),
        (77, 0, 77),
        (-1, -5, -6),
        (-3, 14, 11),
        (13, -50, -37),
    ])
    def test_basic_add(self, any_rpc_client, term_a, term_b, expected_result):
        assert any_rpc_client.call("add", term_a, term_b) == expected_result


class TestSystemMethods:
    def test_list_methods(self, any_rpc_client):
        result = any_rpc_client.call("system.listMethods")
        assert type(result) == list
        assert len(result) > 1
        assert 'system.listMethods' in result
        assert 'divide' in result
        assert 'customized_name' in result

    def test_get_signature_empty(self, any_rpc_client):
        signature = any_rpc_client.call('system.methodSignature', 'add')
        # This one doesn't have any docstring defined
        assert type(signature) == list
        assert len(signature) == 0

    def test_get_signature(self, any_rpc_client):
        signature = any_rpc_client.call('system.methodSignature', 'divide')
        # divide() rpc method has 2 parameters used to perform the division. It also have 6 unused parameters (to
        # test arguments ordering in another test). Return type + 8 parameters = 9 elements in the signature
        assert type(signature) == list
        assert len(signature) == 9
        # Return type
        assert signature[0] == 'int or double'
        # numerator & denominator
        assert signature[1] == 'int or double'
        assert signature[2] == 'int or double'
        # Additional arguments (unused in method): x, y, z, a, b, c
        assert signature[3] == 'str'
        assert signature[4] == 'bytes'
        assert signature[5] == 'list'
        assert signature[6] == 'float'
        assert signature[7] == 'int'
        assert signature[8] == 'int'

    def test_get_signature_3(self, any_rpc_client):
        exc_match = r'Invalid parameters: Unknown method nonexistent_method. Unable to retrieve signature.'
        with pytest.raises(any_rpc_client.error_response_exception, match=exc_match) as exc_info:
            any_rpc_client.call('system.methodSignature', 'nonexistent_method')
        any_rpc_client.assert_exception_code(exc_info.value, RPC_INVALID_PARAMS)

    def test_method_help_with_doc(self, any_rpc_client):
        help_text = any_rpc_client.call('system.methodHelp', "divide")
        assert 'Divide a numerator by a denominator' in help_text

    def test_method_help_no_doc(self, any_rpc_client):
        help_text = any_rpc_client.call('system.methodHelp', "add")
        assert type(help_text) == str
        assert help_text == ''

    def test_method_help_invalid_method(self, any_rpc_client):
        exc_match = r'Invalid parameters: Unknown method nonexistent_method. Unable to retrieve signature.'
        with pytest.raises(any_rpc_client.error_response_exception, match=exc_match) as exc_info:
            any_rpc_client.call('system.methodSignature', 'nonexistent_method')
        any_rpc_client.assert_exception_code(exc_info.value, RPC_INVALID_PARAMS)
