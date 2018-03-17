# coding: utf-8
import pytest
from django.contrib.auth.models import Permission, Group, AnonymousUser


@pytest.fixture
def add_user_perm(db):
    return Permission.objects.get(codename='add_user')


@pytest.fixture
def change_user_perm(db):
    return Permission.objects.get(codename='change_user')


@pytest.fixture
def delete_user_perm(db):
    return Permission.objects.get(codename='delete_user')


COMMON_PASSWORD = '123456'


@pytest.fixture
def anonymous_user(transactional_db):
    return AnonymousUser()


@pytest.fixture
def john_doe(django_user_model, transactional_db):
    return django_user_model.objects.create_user('johndoe', email='jd@example.com', password=COMMON_PASSWORD)


@pytest.fixture
def superuser(django_user_model, transactional_db):
    return django_user_model.objects.create_superuser('admin', email='admin@example.com', password=COMMON_PASSWORD)


@pytest.fixture
def common_pwd():
    return COMMON_PASSWORD


@pytest.fixture
def group_A(transactional_db):
    group, _ = Group.objects.get_or_create(name='A')
    return group


@pytest.fixture
def group_B(transactional_db):
    group, _ = Group.objects.get_or_create(name='B')
    return group
