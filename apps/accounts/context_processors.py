from .services import get_user_branch, is_admin, is_manager, is_operator, user_is_global


def permissions(request):
    """Права текущего пользователя для использования в шаблонах."""
    user = request.user
    return {
        "is_admin": is_admin(user),
        "is_manager": is_manager(user),
        "is_operator": is_operator(user),
        "user_is_global": user_is_global(user),
        "user_branch": get_user_branch(user),
        "can_edit": is_admin(user) or is_operator(user),
    }