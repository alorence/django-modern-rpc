# coding: utf-8
import pytest
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType


@pytest.fixture
def auth_permissions(transactional_db):
    # Sometimes, permissions for User model are found in the DB when a test start, sometimes they aren't.
    # I was not able to understand why. It's probably related to the live_server fixture which implies
    # transactional DB use, but this bug was very hard to address.
    # As a workaround, we call get_or_create() for each needed permission. This code is not particularly nice,
    # but it works... at this time.

    user_content_type = ContentType.objects.get(app_label='auth', model='user')

    p1, _ = Permission.objects.get_or_create(content_type=user_content_type,
                                             codename='delete_user', name="Can delete user")

    p2, _ = Permission.objects.get_or_create(content_type=user_content_type,
                                             codename='add_user', name="Can add user")

    p3, _ = Permission.objects.get_or_create(content_type=user_content_type,
                                             codename='change_user', name="Can change user")

    return p1, p2, p3


@pytest.fixture
def john_doe(django_user_model, transactional_db):
    return django_user_model.objects.create_user('johndoe', email='jd@example.com', password='123456')


@pytest.fixture
def superuser(django_user_model, transactional_db):
    return django_user_model.objects.create_superuser('admin', email='admin@example.com', password='123456')


@pytest.fixture
def group_A(transactional_db):
    group, _ = Group.objects.get_or_create(name='A')
    return group


@pytest.fixture
def group_B(transactional_db):
    group, _ = Group.objects.get_or_create(name='B')
    return group
