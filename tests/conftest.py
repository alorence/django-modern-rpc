# coding: utf-8
import pytest
from django.contrib.auth.models import AnonymousUser, Permission, Group


@pytest.fixture(scope="session")
def common_pwd():
    """The default password, used to create any user"""
    return "123456789!"


@pytest.fixture(scope="session")
def anonymous_user():
    return AnonymousUser()


@pytest.fixture(scope="function")
def john_doe(django_user_model, common_pwd):
    """Create and return a standard Django user"""
    return django_user_model.objects.create_user(
        "johndoe", email="jd@example.com", password=common_pwd
    )


@pytest.fixture(scope="function")
def superuser(django_user_model, common_pwd):
    """Create and return a Django superuser"""
    return django_user_model.objects.create_superuser(
        "admin", email="admin@example.com", password=common_pwd
    )


@pytest.fixture(scope="function")
def group_a(db):
    """Return a group named 'A'. Create it if necessary"""
    group, _ = Group.objects.get_or_create(name="A")
    return group


@pytest.fixture(scope="function")
def group_b(db):
    """Return a group named 'B'. Create it if necessary"""
    group, _ = Group.objects.get_or_create(name="B")
    return group


@pytest.fixture(scope="function")
def add_user_perm(db):
    """Return permission 'auth.add_user'"""
    return Permission.objects.get(codename="add_user")


@pytest.fixture(scope="function")
def change_user_perm(db):
    """Return permission 'auth.change_user'"""
    return Permission.objects.get(codename="change_user")


@pytest.fixture(scope="function")
def delete_user_perm(db):
    """Return permission 'auth.delete_user'"""
    return Permission.objects.get(codename="delete_user")
