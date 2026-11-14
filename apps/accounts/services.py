from .models import ROLE_ADMIN, ROLE_MANAGER, ROLE_OPERATOR, Branch


def get_role(user):
    """Роль пользователя, суперпользователь считается администратором."""
    if not user.is_authenticated:
        return None
    if user.is_superuser:
        return ROLE_ADMIN
    profile = getattr(user, "profile", None)
    return getattr(profile, "role", None)


def is_admin(user):
    return get_role(user) == ROLE_ADMIN


def is_manager(user):
    return get_role(user) == ROLE_MANAGER


def is_operator(user):
    return get_role(user) == ROLE_OPERATOR


def get_user_branch(user):
    """Площадка пользователя или None, если доступ ко всем."""
    profile = getattr(user, "profile", None)
    if profile and profile.role == ROLE_OPERATOR:
        return profile.branch
    return None


def get_access(user):
    """
    Возвращает (allowed, branch) для фильтрации данных:
    allowed=False означает, что пользователь не имеет доступа ни к каким площадкам.
    """
    if not user.is_authenticated:
        return False, None
    if user.is_superuser:
        return True, None
    profile = getattr(user, "profile", None)
    if profile is None:
        return False, None
    if profile.role in (ROLE_ADMIN, ROLE_MANAGER):
        return True, None
    if profile.role == ROLE_OPERATOR:
        if profile.branch is None:
            return False, None
        return True, profile.branch
    return False, None


def get_visible_branches(user):
    """Список площадок, доступных пользователю."""
    branch = get_user_branch(user)
    if branch is not None:
        return Branch.objects.filter(pk=branch.pk)
    return Branch.objects.all()


def user_is_global(user):
    """Имеет ли пользователь доступ ко всем площадкам (admin/manager)."""
    return is_admin(user) or is_manager(user)