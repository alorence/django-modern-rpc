import functools

import django
from django.http import HttpResponseNotAllowed
from django.utils.log import log_response
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

if django.VERSION >= (5, 0):
    # Django updated its decorators to support wrapping asynchronous method in release 5.0
    # REF: https://docs.djangoproject.com/en/5.2/releases/5.0/#decorators

    async_csrf_exempt = csrf_exempt
    async_require_post = require_POST

else:
    # Fore Django version < 5.0, we partially redefine decorators to support async view

    def async_csrf_exempt(view):
        view.csrf_exempt = True
        return view

    def async_require_post(func):
        @functools.wraps(func)
        async def inner(request, *args, **kwargs):
            if request.method != "POST":
                response = HttpResponseNotAllowed([""])
                log_response(
                    "Method Not Allowed (%s): %s",
                    request.method,
                    request.path,
                    response=response,
                    request=request,
                )
                return response
            return await func(request, *args, **kwargs)

        return inner
