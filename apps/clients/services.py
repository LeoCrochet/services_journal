from apps.accounts.services import get_access

from .models import Client


def get_visible_clients(user):
    """Клиенты, доступные пользователю с учётом площадки."""
    allowed, branch = get_access(user)
    queryset = Client.objects.all()
    if not allowed:
        return queryset.none()
    if branch is not None:
        queryset = queryset.filter(branch=branch)
    return queryset
