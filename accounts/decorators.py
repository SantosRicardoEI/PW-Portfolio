from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


def group_required(group_name):
    """Exige autenticação e pertença a um grupo, permitindo superusers."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if not (
                request.user.is_superuser
                or request.user.groups.filter(name=group_name).exists()
            ):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator
