# coding: utf-8
from django.utils import six


DEBUG = True
ALLOWED_HOSTS = ['*']
SECRET_KEY = 'dummy'
ROOT_URLCONF = 'testsite.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'unused',
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

MIDDLEWARE_CLASSES = (
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
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'nullhandler': {
            'level': 'INFO',
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        # Note: We don't want to print logs when executing tests, so no logger is declared for modernrpc module.
        # But since we need some tests for logging utilities, let's declare 2 loggers for non-existent packages
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
        # This seems the only way to hide log messages from jsonrpcclient
        # See https://github.com/bcb/jsonrpcclient/issues/45
        'jsonrpcclient.client.request': {
            'handlers': ['nullhandler'],
            'level': 'INFO',
            'propagate': False,
        },
        'jsonrpcclient.client.response': {
            'handlers': ['nullhandler'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}

if six.PY2:
    MODERNRPC_METHODS_MODULES.append('testsite.rpc_methods_stub.python2_specific')

MODERNRPC_PY2_STR_TYPE = str
