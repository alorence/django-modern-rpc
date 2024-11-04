import pytest

from modernrpc.exceptions import RPC_INTERNAL_ERROR


class TestAuthSuperuser:
    @pytest.fixture
    def client_auth(self, superuser, common_pwd):
        return "basic", superuser.username, common_pwd

    @pytest.mark.parametrize(
        ("method_name", "args", "result"),
        [
            ("display_authenticated_user", [], "username: admin"),
            ("logged_user_required", [5], 5),
            ("logged_user_required_alt", [5], 5),
            ("logged_superuser_required", [5], 5),
            ("logged_superuser_required_alt", [5], 5),
            ("delete_user_perm_required", [5], 5),
            ("any_permission_required", [5], 5),
            ("all_permissions_required", [5], 5),
            ("in_group_a_required", [5], 5),
            ("in_group_a_and_b_required", [5], 5),
            ("in_group_a_and_b_required_alt", [5], 5),
            ("in_group_a_or_b_required", [5], 5),
        ],
    )
    def test_with_superuser(self, any_rpc_client, method_name, args, result):
        assert any_rpc_client.call(method_name, *args) == result

    def test_jsonrpc_batch_request(self, jsonrpc_client):
        result = jsonrpc_client.batch_request(
            [
                ("add", [7, 3]),
                ("logged_superuser_required", [6]),
            ]
        )
        assert isinstance(result, jsonrpc_client.batch_result_klass)
        assert result == [
            {"id": 0, "jsonrpc": "2.0", "result": 10},
            {"id": 1, "jsonrpc": "2.0", "result": 6},
        ]

    def test_xmlrpc_multicall(self, xmlrpc_client):
        result = xmlrpc_client.multicall(
            [
                ("add", [7, 3]),
                ("logged_superuser_required", [3]),
            ]
        )
        assert isinstance(result, xmlrpc_client.multicall_result_klass)
        assert list(result) == [10, 3]


class TestAuthAnonymousUser:
    @pytest.mark.parametrize(
        ("method_name", "args"),
        [
            ("display_authenticated_user", []),
            ("logged_user_required", [5]),
            ("logged_user_required_alt", [5]),
            ("logged_superuser_required", [5]),
            ("logged_superuser_required_alt", [5]),
            ("delete_user_perm_required", [5]),
            ("any_permission_required", [5]),
            ("all_permissions_required", [5]),
            ("in_group_a_required", [5]),
            ("in_group_a_and_b_required", [5]),
            ("in_group_a_and_b_required_alt", [5]),
            ("in_group_a_or_b_required", [5]),
        ],
    )
    def test_with_anonymous_user(self, any_rpc_client, method_name, args):
        # Exception test match
        exc_match = rf'Authentication failed when calling "{method_name}"'
        with pytest.raises(any_rpc_client.auth_error_exception, match=exc_match) as exc_info:
            any_rpc_client.call(method_name, *args)
        any_rpc_client.assert_exception_code(exc_info.value, RPC_INTERNAL_ERROR)

    def test_jsonrpc_batch_request(self, jsonrpc_client):
        result = jsonrpc_client.batch_request(
            [
                ("add", [7, 3]),
                ("logged_superuser_required", [6]),
            ]
        )
        assert isinstance(result, jsonrpc_client.batch_result_klass)
        assert result == [
            {"id": 0, "jsonrpc": "2.0", "result": 10},
            {
                "id": 1,
                "jsonrpc": "2.0",
                "error": {
                    "code": RPC_INTERNAL_ERROR,
                    "message": 'Authentication failed when calling "logged_superuser_required"',
                },
            },
        ]

    def test_xmlrpc_multicall(self, xmlrpc_client):
        result = xmlrpc_client.multicall(
            [
                ("add", [7, 3]),
                ("logged_superuser_required", [3]),
            ]
        )
        assert isinstance(result, xmlrpc_client.multicall_result_klass)
        assert result[0] == 10

        exc_match = r'Authentication failed when calling "logged_superuser_required"'
        with pytest.raises(xmlrpc_client.error_response_exception, match=exc_match) as exc_info:
            assert result[1]
        xmlrpc_client.assert_exception_code(exc_info.value, RPC_INTERNAL_ERROR)


class TestAuthStandardUser:
    @pytest.fixture
    def client_auth(self, john_doe, common_pwd):
        return "basic", john_doe.username, common_pwd

    @pytest.mark.parametrize(
        ("method_name", "args", "must_raise", "result"),
        [
            ("display_authenticated_user", [], False, "username: johndoe"),
            ("logged_user_required", [5], False, 5),
            ("logged_user_required_alt", [5], False, 5),
            # -------------------------------------------------------------
            ("logged_superuser_required", [5], True, None),
            ("logged_superuser_required_alt", [5], True, None),
            ("delete_user_perm_required", [5], True, None),
            ("any_permission_required", [5], True, None),
            ("all_permissions_required", [5], True, None),
            ("in_group_a_required", [5], True, None),
            ("in_group_a_and_b_required", [5], True, None),
            ("in_group_a_and_b_required_alt", [5], True, None),
            ("in_group_a_or_b_required", [5], True, None),
        ],
    )
    def test_with_standard_user(self, any_rpc_client, method_name, args, must_raise, result):
        if must_raise:
            # Exception test match
            exc_match = rf'Authentication failed when calling "{method_name}"'
            with pytest.raises(any_rpc_client.auth_error_exception, match=exc_match) as exc_info:
                any_rpc_client.call(method_name, *args)
            any_rpc_client.assert_exception_code(exc_info.value, RPC_INTERNAL_ERROR)
        else:
            assert any_rpc_client.call(method_name, *args) == result

    def test_permissions_updates(
        self,
        any_rpc_client,
        john_doe,
        delete_user_perm,
        add_user_perm,
        change_user_perm,
    ):
        john_doe.user_permissions.add(delete_user_perm)

        assert any_rpc_client.call("delete_user_perm_required", 5) == 5
        assert any_rpc_client.call("any_permission_required", 5) == 5

        exc_match = r'Authentication failed when calling "all_permissions_required"'
        with pytest.raises(any_rpc_client.auth_error_exception, match=exc_match) as exc_info:
            assert any_rpc_client.call("all_permissions_required", 5)
        any_rpc_client.assert_exception_code(exc_info.value, RPC_INTERNAL_ERROR)

        john_doe.user_permissions.add(add_user_perm, change_user_perm)
        assert any_rpc_client.call("all_permissions_required", 5) == 5

    def test_group_memberships_updates(self, any_rpc_client, john_doe, group_a, group_b):
        john_doe.groups.add(group_a)

        assert any_rpc_client.call("in_group_a_required", 5) == 5
        assert any_rpc_client.call("in_group_a_or_b_required", 5) == 5

        exc_match = r'Authentication failed when calling "in_group_a_and_b_required"'
        with pytest.raises(any_rpc_client.auth_error_exception, match=exc_match) as exc_info:
            assert any_rpc_client.call("in_group_a_and_b_required", 5)
        any_rpc_client.assert_exception_code(exc_info.value, RPC_INTERNAL_ERROR)

        exc_match = r'Authentication failed when calling "in_group_a_and_b_required_alt"'
        with pytest.raises(any_rpc_client.auth_error_exception, match=exc_match) as exc_info:
            assert any_rpc_client.call("in_group_a_and_b_required_alt", 5)
        any_rpc_client.assert_exception_code(exc_info.value, RPC_INTERNAL_ERROR)

        john_doe.groups.add(group_a, group_b)
        assert any_rpc_client.call("in_group_a_and_b_required", 5) == 5
        assert any_rpc_client.call("in_group_a_and_b_required_alt", 5) == 5

    def test_custom_predicate_allowed(self, any_rpc_client):
        assert any_rpc_client.call("get_user_agent")

    def test_custom_predicate_rejected(self, any_rpc_client):
        exc_match = r'Authentication failed when calling "power_2"'
        with pytest.raises(any_rpc_client.auth_error_exception, match=exc_match) as exc_info:
            assert any_rpc_client.call("power_2", 5)
        any_rpc_client.assert_exception_code(exc_info.value, RPC_INTERNAL_ERROR)
