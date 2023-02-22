import pytest
from django.core.exceptions import ImproperlyConfigured

from modernrpc.views import RPCEntryPoint


def test_invalid_entry_point_no_handler(settings, rf):
    settings.MODERNRPC_HANDLERS = []
    entry_point = RPCEntryPoint.as_view()

    exc_match = r"At least 1 handler must be instantiated"
    with pytest.raises(ImproperlyConfigured, match=exc_match):
        entry_point(rf.post("xxx"))
