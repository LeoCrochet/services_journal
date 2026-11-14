from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import ROLE_ADMIN, ROLE_MANAGER
from .services import get_role


def role_required(*roles):
    """Доступ только для перечисленных ролей (после входа в систему)."""

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if get_role(request.user) not in roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


admin_required = role_required(ROLE_ADMIN)
manager_or_admin = role_required(ROLE_MANAGER, ROLE_ADMIN)