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
    # We add a non existant module, so auto-registering will print a warning
    # This increase the coverage ratio in apps.py
    'inexistant.module',
]
