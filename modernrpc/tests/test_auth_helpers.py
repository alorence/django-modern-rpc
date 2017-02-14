import pytest
import pytest_django
from django.contrib.auth.models import AnonymousUser, Permission
from django.contrib.contenttypes.models import ContentType

from modernrpc.auth import user_is_logged, user_is_superuser, user_has_perm, user_has_perms


def test_user_is_logged(anonymous_user, john_doe, superuser):

    assert user_is_logged(anonymous_user) is False
    assert user_is_logged(john_doe) is True
    assert user_is_logged(superuser) is True


def test_user_is_superuser(anonymous_user, john_doe, superuser):

    assert user_is_superuser(anonymous_user) is False
    assert user_is_superuser(john_doe) is False
    assert user_is_superuser(superuser) is True


def test_user_has_perm(anonymous_user, john_doe, superuser, auth_permissions):

    p = auth_permissions[0]

    assert user_has_perm(anonymous_user, p) is False
    assert user_has_perm(john_doe, p) is False
    assert user_has_perm(superuser, p) is True

    john_doe.user_permissions.add(p)
    assert user_has_perm(john_doe, p) is True


def test_user_has_perms(anonymous_user, john_doe, superuser, auth_permissions):

    perms = auth_permissions[0], auth_permissions[1]

    assert user_has_perms(anonymous_user, perms) is False
    assert user_has_perms(john_doe, perms) is False
    assert user_has_perms(superuser, perms) is True

    john_doe.user_permissions.add(auth_permissions[0])
    assert user_has_perms(john_doe, perms) is False

    john_doe.user_permissions.add(auth_permissions[1])
    assert user_has_perms(john_doe, perms) is True



