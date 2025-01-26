from pathlib import Path

DEBUG = True
ALLOWED_HOSTS = ["*"]
SECRET_KEY = "dummy"
ROOT_URLCONF = "testsite.urls"

SITE_ROOT = Path(__file__).parent

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "file::memory:",
    },
}

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.sites",
    "django.contrib.sessions",
    "django.contrib.contenttypes",
    "modernrpc",
)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
            "loaders": [
                "django.template.loaders.app_directories.Loader",
            ],
        },
    },
]

MIDDLEWARE = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
)

# Prevent a warning with recent Django versions
USE_TZ = False

STATIC_ROOT = ""
STATIC_URL = "/"

MODERNRPC_LOG_EXCEPTIONS = False
