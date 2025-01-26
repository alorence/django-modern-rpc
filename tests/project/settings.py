DEBUG = True
ALLOWED_HOSTS = ["*"]
SECRET_KEY = "dummy-tests"
ROOT_URLCONF = "tests.project.urls"
APPEND_SLASH = False

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
)

MIDDLEWARE = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
)

USE_TZ = True

STATIC_ROOT = ""
STATIC_URL = "/"
