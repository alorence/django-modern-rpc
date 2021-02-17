# coding: utf-8
import os
from os.path import dirname, realpath, join

import six

DEBUG = True
ALLOWED_HOSTS = ['*']
SECRET_KEY = 'dummy'
ROOT_URLCONF = 'testsite.urls'

SITE_ROOT = dirname(realpath(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        # Using :memory: SQLIte DB cause a Segmentation Fault on Travis-CI server
        # To prevent such error, we prefer using a true file-based DB.
        # Another solution would be to use Travis Postgres or Mysql instance, but in that case
        # we would need a different settings between local test environment and CI server one.
        'NAME': os.path.join(SITE_ROOT, 'modernrpc-test.db'),
        'TEST': {'NAME': os.path.join(SITE_ROOT, 'modernrpc-test.db')}
    },
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.sessions',
    'django.contrib.contenttypes',

    'modernrpc',

    'testsite.rpc_methods_stub',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]

MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

MEDIA_ROOT = ''
MEDIA_URL = '/'
STATIC_ROOT = ''
STATIC_URL = '/'

MODERNRPC_METHODS_MODULES = [
    'testsite.rpc_methods_stub.generic',
    'testsite.rpc_methods_stub.specific_types',
    'testsite.rpc_methods_stub.specific_protocol',
    'testsite.rpc_methods_stub.with_authentication',
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'default': {
            'format': "[%(asctime)s] %(levelname)s [%(filename)s:%(funcName)s:%(lineno)s] %(message)s",
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'nullhandler': {
            'level': 'INFO',
            'class': 'logging.NullHandler',
        },
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': join(SITE_ROOT, 'modernrpc.log'),
            'maxBytes': 1024 * 1024 * 1,  # 1 MB
            'formatter': 'default',
            'backupCount': 5,
            # In Django 1.11, without this attribute, a warning is thrown at server startup
            # Use `python -Wall ./manage.py runserver` to see warnings
            # See https://stackoverflow.com/a/30684667/1887976 for more info
            'delay': True,
        },
    },
    'loggers': {
        # Default modernrpc logger. Will collect test execution logs into modernrpc/tests/testsite/modernrpc.log
        'modernrpc': {
            'handlers': ['logfile'],
            'level': 'INFO',
            'propagate': False,
        },
        # test_logging.py will execute some tests on logging utilities (get_modernrpc_logger() and
        # logger_has_handlers()). These dummy loggers are declared here
        # See test_logging.py
        'my_app': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': True,
        },
        'my_app.a': {
            'handlers': [],
            'level': 'INFO',
            'propagate': False,
        },
    }
}

if six.PY2:
    MODERNRPC_METHODS_MODULES.append('testsite.rpc_methods_stub.python2_specific')

MODERNRPC_PY2_STR_TYPE = str
MODERNRPC_LOG_EXCEPTIONS = False
