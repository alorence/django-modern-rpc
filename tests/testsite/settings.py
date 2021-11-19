# coding: utf-8
from os.path import dirname, realpath

DEBUG = True
ALLOWED_HOSTS = ['*']
SECRET_KEY = 'dummy'
ROOT_URLCONF = 'testsite.urls'

SITE_ROOT = dirname(realpath(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': "file::memory:",
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

STATIC_ROOT = ''
STATIC_URL = '/'

MODERNRPC_METHODS_MODULES = [
    'testsite.rpc_methods_stub.generic',
    'testsite.rpc_methods_stub.specific_types',
    'testsite.rpc_methods_stub.specific_protocol',
    'testsite.rpc_methods_stub.with_authentication',
]

MODERNRPC_LOG_EXCEPTIONS = False
