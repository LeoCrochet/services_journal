from apps.accounts.services import get_user_branch

from .models import Client


def get_visible_clients(user):
    """Клиенты, доступные пользователю с учётом площадки."""
    branch = get_user_branch(user)
    queryset = Client.objects.all()
    if branch is not None:
        queryset = queryset.filter(branch=branch)
    return queryset