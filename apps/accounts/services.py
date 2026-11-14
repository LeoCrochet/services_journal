from .models import ROLE_ADMIN, ROLE_MANAGER, ROLE_OPERATOR, Branch


def is_admin(user):
    return user.is_authenticated and getattr(user, "profile", None) and user.profile.role == ROLE_ADMIN


def is_manager(user):
    return user.is_authenticated and getattr(user, "profile", None) and user.profile.role == ROLE_MANAGER


def is_operator(user):
    return user.is_authenticated and getattr(user, "profile", None) and user.profile.role == ROLE_OPERATOR


def get_user_branch(user):
    """Площадка пользователя или None, если доступ ко всем."""
    profile = getattr(user, "profile", None)
    if profile and profile.role == ROLE_OPERATOR:
        return profile.branch
    return None


def get_visible_branches(user):
    """Список площадок, доступных пользователю."""
    branch = get_user_branch(user)
    if branch is not None:
        return Branch.objects.filter(pk=branch.pk)
    return Branch.objects.all()


def user_is_global(user):
    """Имеет ли пользователь доступ ко всем площадкам (admin/manager)."""
    return is_admin(user) or is_manager(user)