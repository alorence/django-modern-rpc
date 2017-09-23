# coding: utf-8
from django.http.request import HttpRequest
from pytest import raises

from modernrpc.auth import user_is_authenticated, user_is_superuser, user_has_perm, user_has_all_perms, user_in_group, \
    user_has_any_perm, user_in_all_groups, user_in_any_group, user_is_anonymous
from modernrpc.auth.basic import http_basic_auth_get_user


def test_user_is_authenticated(anonymous_user, john_doe, superuser):

    assert user_is_authenticated(superuser)
    assert not user_is_authenticated(anonymous_user)
    assert user_is_authenticated(john_doe)


def test_user_is_anonymous(anonymous_user, john_doe, superuser):

    assert not user_is_anonymous(superuser)
    assert user_is_anonymous(anonymous_user)
    assert not user_is_anonymous(john_doe)


def test_user_is_superuser(anonymous_user, john_doe, superuser):

    assert user_is_superuser(superuser)
    assert not user_is_superuser(anonymous_user)
    assert not user_is_superuser(john_doe)


def test_user_has_perm(django_user_model, anonymous_user, john_doe, superuser, delete_user_perm):

    perm_str = '{}.{}'.format('auth', delete_user_perm.codename)

    # Superuser always virtually have permissions
    assert user_has_perm(superuser, perm_str) is True

    # Ensure permissions are correctly set by default
    assert user_has_perm(anonymous_user, perm_str) is False
    assert user_has_perm(john_doe, perm_str) is False

    # Set permissions to normal user
    john_doe.user_permissions.add(delete_user_perm)

    # Re-fetch user from DB, so cached permissions are updated from DB.
    # See https://docs.djangoproject.com/en/1.10/topics/auth/default/#permission-caching
    john_doe = django_user_model.objects.get(username=john_doe.username)
    # And check the method now returns True
    assert user_has_perm(john_doe, perm_str) is True


def test_user_has_perms(django_user_model, anonymous_user, john_doe, superuser, delete_user_perm, add_user_perm):

    perms_str = [
        '{}.{}'.format('auth', p.codename) for p in [delete_user_perm, add_user_perm]
    ]

    # Superuser always virtually have permissions
    assert user_has_all_perms(superuser, perms_str) is True

    # Ensure permissions are correctly set by default
    assert user_has_all_perms(anonymous_user, perms_str) is False
    assert user_has_all_perms(john_doe, perms_str) is False

    # Set 1 permissions to normal user
    john_doe.user_permissions.add(delete_user_perm)
    # Re-fetch user from DB, so cached permissions are updated from DB.
    # See https://docs.djangoproject.com/en/1.10/topics/auth/default/#permission-caching
    john_doe = django_user_model.objects.get(username=john_doe.username)
    # The user still don't have enough permissions
    assert user_has_all_perms(john_doe, perms_str) is False

    # Now it's OK
    john_doe.user_permissions.add(add_user_perm)
    john_doe = django_user_model.objects.get(username=john_doe.username)
    assert user_has_all_perms(john_doe, perms_str) is True


def test_user_has_any_perm(django_user_model, anonymous_user, john_doe, superuser, delete_user_perm, add_user_perm):

    perms_str = [
        '{}.{}'.format('auth', p.codename) for p in [delete_user_perm, add_user_perm]
    ]

    # Superuser always virtually have permissions
    assert user_has_any_perm(superuser, perms_str) is True

    # Ensure permissions are correctly set by default
    assert user_has_any_perm(anonymous_user, perms_str) is False
    assert user_has_any_perm(john_doe, perms_str) is False

    # Set both permissions to normal user
    john_doe.user_permissions.add(delete_user_perm, add_user_perm)
    # Re-fetch user from DB, so cached permissions are updated from DB.
    # See https://docs.djangoproject.com/en/1.10/topics/auth/default/#permission-caching
    john_doe = django_user_model.objects.get(username=john_doe.username)
    # The user still don't have enough permissions
    assert user_has_any_perm(john_doe, perms_str) is True

    # Remove 1 permission, still OK
    john_doe.user_permissions.remove(delete_user_perm)
    john_doe = django_user_model.objects.get(username=john_doe.username)
    assert user_has_any_perm(john_doe, perms_str) is True


def test_user_in_group_invalid_args(group_A, john_doe):
    with raises(TypeError):
        user_in_group(john_doe, group_A.id)


def test_user_in_group(group_A, anonymous_user, john_doe, superuser):

    # Superuser always virtually have permissions
    assert user_in_group(superuser, group_A) is True

    # By default, users are not in any group
    assert user_in_group(anonymous_user, group_A) is False
    assert user_in_group(john_doe, group_A) is False

    john_doe.groups.add(group_A)
    assert user_in_group(john_doe, group_A) is True


def test_user_in_group_str(group_A, anonymous_user, john_doe, superuser):

    # Superuser always virtually have permissions
    assert user_in_group(superuser, group_A.name) is True

    # By default, users are not in any group
    assert user_in_group(anonymous_user, group_A.name) is False
    assert user_in_group(john_doe, group_A.name) is False

    john_doe.groups.add(group_A)
    assert user_in_group(john_doe, group_A.name) is True


def test_user_in_any_group(group_A, group_B, anonymous_user, john_doe, superuser):

    groups = [group_A, group_B]

    # Superuser always virtually have permissions
    assert user_in_any_group(superuser, groups) is True

    # By default, users are not in any group
    assert user_in_any_group(anonymous_user, groups) is False
    assert user_in_any_group(john_doe, groups) is False

    john_doe.groups.add(group_A)
    assert user_in_any_group(john_doe, groups) is True

    john_doe.groups.add(group_B)
    assert user_in_any_group(john_doe, groups) is True

    john_doe.groups.clear()
    assert user_in_any_group(john_doe, groups) is False


def test_user_in_any_group_str(group_A, group_B, anonymous_user, john_doe, superuser):

    groups = ['A', 'B']

    # Superuser always virtually have permissions
    assert user_in_any_group(superuser, groups) is True

    # By default, users are not in any group
    assert user_in_any_group(anonymous_user, groups) is False
    assert user_in_any_group(john_doe, groups) is False

    john_doe.groups.add(group_A)
    assert user_in_any_group(john_doe, groups) is True

    john_doe.groups.add(group_B)
    assert user_in_any_group(john_doe, groups) is True

    john_doe.groups.clear()
    assert user_in_any_group(john_doe, groups) is False


def test_user_in_all_groups(group_A, group_B, anonymous_user, john_doe, superuser):

    groups = [group_A, group_B]

    # Superuser always virtually have permissions
    assert user_in_all_groups(superuser, groups) is True

    # By default, users are not in any group
    assert user_in_all_groups(anonymous_user, groups) is False
    assert user_in_all_groups(john_doe, groups) is False

    john_doe.groups.add(group_A)
    assert user_in_all_groups(john_doe, groups) is False

    john_doe.groups.add(group_B)
    assert user_in_all_groups(john_doe, groups) is True

    john_doe.groups.clear()
    assert user_in_all_groups(john_doe, groups) is False


def test_user_in_all_groups_str(group_A, group_B, anonymous_user, john_doe, superuser):

    groups = ['A', 'B']

    # Superuser always virtually have permissions
    assert user_in_all_groups(superuser, groups) is True

    # By default, users are not in any group
    assert user_in_all_groups(anonymous_user, groups) is False
    assert user_in_all_groups(john_doe, groups) is False

    john_doe.groups.add(group_A)
    assert user_in_all_groups(john_doe, groups) is False

    john_doe.groups.add(group_B)
    assert user_in_all_groups(john_doe, groups) is True

    john_doe.groups.clear()
    assert user_in_all_groups(john_doe, groups) is False


def test_http_basic_get_user():

    # Basic django request, without authentication info
    request = HttpRequest()

    # Standard middlewares were not applied on this request
    user = http_basic_auth_get_user(request)

    assert user is not None
    assert user_is_anonymous(user)
