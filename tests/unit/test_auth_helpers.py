import pytest
from django.http.request import HttpRequest

from modernrpc.auth import (
    user_has_all_perms,
    user_has_any_perm,
    user_has_perm,
    user_in_all_groups,
    user_in_any_group,
    user_in_group,
    user_is_anonymous,
    user_is_authenticated,
    user_is_superuser,
)
from modernrpc.auth.basic import http_basic_auth_get_user


class TestAuthentication:
    def test_user_is_authenticated(self, anonymous_user, john_doe, superuser):
        assert not user_is_authenticated(anonymous_user)
        assert user_is_authenticated(john_doe)
        assert user_is_authenticated(superuser)

    def test_user_is_anonymous(self, anonymous_user, john_doe, superuser):
        assert user_is_anonymous(anonymous_user)
        assert not user_is_anonymous(john_doe)
        assert not user_is_anonymous(superuser)

    def test_user_is_superuser(self, anonymous_user, john_doe, superuser):
        assert not user_is_superuser(anonymous_user)
        assert not user_is_superuser(john_doe)
        assert user_is_superuser(superuser)

    def test_http_basic_get_user(
        self,
    ):
        # Basic django request, without authentication info
        request = HttpRequest()

        # Standard middlewares were not applied on this request
        user = http_basic_auth_get_user(request)

        assert user is not None
        assert user_is_anonymous(user)


class TestPermissions:
    @staticmethod
    def permission_string(perm):
        return f"{perm.content_type.app_label}.{perm.codename}"

    def test_default_permissions(self, superuser, anonymous_user, john_doe, delete_user_perm, add_user_perm):
        perm = self.permission_string(delete_user_perm)

        # Superuser always virtually have permissions
        assert user_has_perm(superuser, perm) is True
        # Ensure permissions are correctly set by default
        assert user_has_perm(anonymous_user, perm) is False
        assert user_has_perm(john_doe, perm) is False

        perms = [self.permission_string(perm) for perm in [delete_user_perm, add_user_perm]]

        # Superuser always virtually have permissions
        assert user_has_all_perms(superuser, perms) is True
        # Ensure permissions are correctly set by default
        assert user_has_all_perms(anonymous_user, perms) is False
        assert user_has_all_perms(john_doe, perms) is False

        # Superuser always virtually have permissions
        assert user_has_any_perm(superuser, perms) is True
        # Ensure permissions are correctly set by default
        assert user_has_any_perm(anonymous_user, perms) is False
        assert user_has_any_perm(john_doe, perms) is False

    def test_user_has_perm(self, django_user_model, john_doe, delete_user_perm):
        # Set permissions to normal user
        john_doe.user_permissions.add(delete_user_perm)
        # Re-fetch user from DB, so cached permissions are updated from DB.
        # See https://docs.djangoproject.com/en/3.2/topics/auth/default/#permission-caching
        john_doe = django_user_model.objects.get(username=john_doe.username)

        # And check the permission is granted
        assert user_has_perm(john_doe, self.permission_string(delete_user_perm)) is True

    def test_user_has_all_perms(self, django_user_model, john_doe, delete_user_perm, add_user_perm):
        perms = [self.permission_string(perm) for perm in [delete_user_perm, add_user_perm]]

        # Set 1 permissions to normal user
        john_doe.user_permissions.add(delete_user_perm)
        # Re-fetch user from DB, so cached permissions are updated from DB.
        # See https://docs.djangoproject.com/en/3.2/topics/auth/default/#permission-caching
        john_doe = django_user_model.objects.get(username=john_doe.username)
        # The user still don't have enough permissions
        assert user_has_all_perms(john_doe, perms) is False

        # Now it's OK
        john_doe.user_permissions.add(add_user_perm)
        john_doe = django_user_model.objects.get(username=john_doe.username)
        assert user_has_all_perms(john_doe, perms) is True

    def test_user_has_any_perm(self, django_user_model, john_doe, delete_user_perm, add_user_perm):
        perms = [self.permission_string(perm) for perm in [delete_user_perm, add_user_perm]]

        # Set both permissions to normal user
        john_doe.user_permissions.add(delete_user_perm, add_user_perm)
        # Re-fetch user from DB, so cached permissions are updated from DB.
        # See https://docs.djangoproject.com/en/3.2/topics/auth/default/#permission-caching
        john_doe = django_user_model.objects.get(username=john_doe.username)
        # The user still don't have enough permissions
        assert user_has_any_perm(john_doe, perms) is True

        # Remove 1 permission, still OK
        john_doe.user_permissions.remove(delete_user_perm)
        john_doe = django_user_model.objects.get(username=john_doe.username)
        assert user_has_any_perm(john_doe, perms) is True

    def test_user_in_group_invalid_args(self, group_a, john_doe):
        exc_match = r"'group' argument must be a string or a Group instance"
        with pytest.raises(TypeError, match=exc_match):
            user_in_group(john_doe, group_a.id)


class TestGroups:
    def test_anonymous_and_superuser_groups(self, group_a, group_b, anonymous_user, superuser):
        groups = [group_a, group_b]
        groups_str = [group_a.name, group_b.name]

        # Superuser always virtually have permissions
        assert user_in_group(superuser, group_a) is True
        assert user_in_group(superuser, group_a.name) is True
        assert user_in_any_group(superuser, groups) is True
        assert user_in_any_group(superuser, groups_str) is True
        assert user_in_all_groups(superuser, groups) is True
        assert user_in_all_groups(superuser, groups_str) is True

        # By default, anonymous users are not in any group
        assert user_in_group(anonymous_user, group_a) is False
        assert user_in_group(anonymous_user, group_a.name) is False
        assert user_in_any_group(anonymous_user, groups) is False
        assert user_in_any_group(anonymous_user, groups_str) is False
        assert user_in_all_groups(anonymous_user, groups) is False
        assert user_in_all_groups(anonymous_user, groups_str) is False

    def test_user_in_group(self, group_a, john_doe):
        # By default, users are not in any group
        assert user_in_group(john_doe, group_a) is False
        assert user_in_group(john_doe, group_a.name) is False

        john_doe.groups.add(group_a)
        assert user_in_group(john_doe, group_a) is True
        assert user_in_group(john_doe, group_a.name) is True

    def test_user_in_any_group(self, group_a, group_b, john_doe):
        groups = [group_a, group_b]
        groups_str = [group_a.name, group_b.name]

        # By default, users are not in any group
        assert user_in_any_group(john_doe, groups) is False
        assert user_in_any_group(john_doe, groups_str) is False

        john_doe.groups.add(group_a)
        assert user_in_any_group(john_doe, groups) is True
        assert user_in_any_group(john_doe, groups_str) is True

        john_doe.groups.add(group_b)
        assert user_in_any_group(john_doe, groups) is True
        assert user_in_any_group(john_doe, groups_str) is True

        john_doe.groups.clear()
        assert user_in_any_group(john_doe, groups) is False
        assert user_in_any_group(john_doe, groups_str) is False

    def test_user_in_all_groups(self, group_a, group_b, john_doe):
        groups = [group_a, group_b]
        groups_str = [group_a.name, group_b.name]

        # By default, users are not in any group
        assert user_in_all_groups(john_doe, groups) is False
        assert user_in_all_groups(john_doe, groups_str) is False

        john_doe.groups.add(group_a)
        assert user_in_all_groups(john_doe, groups) is False
        assert user_in_all_groups(john_doe, groups_str) is False

        john_doe.groups.add(group_b)
        assert user_in_all_groups(john_doe, groups) is True
        assert user_in_all_groups(john_doe, groups_str) is True

        john_doe.groups.clear()
        assert user_in_all_groups(john_doe, groups) is False
        assert user_in_all_groups(john_doe, groups_str) is False
