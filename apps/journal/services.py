from apps.accounts.services import get_access

from .models import Order


def get_visible_orders(user):
    """Заявки, доступные пользователю с учётом площадки."""
    allowed, branch = get_access(user)
    queryset = Order.objects.select_related("client", "branch")
    if not allowed:
        return queryset.none()
    if branch is not None:
        queryset = queryset.filter(branch=branch)
    return queryset


def generate_order_number(order):
    """Номер вида <PREFIX>-000001, сквозной в рамках площадки."""
    if order.number:
        return order.number

    branch = order.branch
    last = (
        Order.objects.filter(branch=branch, number_seq__isnull=False)
        .order_by("-number_seq")
        .values_list("number_seq", flat=True)
        .first()
    )
    next_seq = (last or 0) + 1
    order.number_seq = next_seq
    order.number = f"{branch.prefix}-{next_seq:06d}"
    return order.number


def assign_order_number(order, save=True):
    """Присваивает номер заявке и сохраняет при необходимости."""
    generate_order_number(order)
    if save:
        order.save(update_fields=["number", "number_seq"])
    return order