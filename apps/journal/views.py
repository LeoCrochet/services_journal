from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.services import get_user_branch
from apps.services.models import Service

from .forms import OrderForm, OrderItemFormSet
from .models import Order
from .services import assign_order_number, get_visible_orders


@login_required
def list_view(request):
    query = request.GET.get("q", "").strip()
    orders = get_visible_orders(request.user)
    if query:
        orders = orders.filter(client__fio__icontains=query)
    return render(request, "journal/list.html", {"orders": orders, "query": query})


def _services_data():
    return list(Service.objects.values("id", "name", "description", "price"))


def _order_form(request, instance=None):
    return OrderForm(request.POST or None, instance=instance, user=request.user)


def _order_context(request, form, formset, order=None):
    return {
        "form": form,
        "formset": formset,
        "services_data": _services_data(),
        "order": order,
    }


@login_required
def create_view(request):
    if request.method == "POST":
        form = _order_form(request)
        formset = OrderItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            order = form.save(commit=False)
            # Оператору принудительно ставим его площадку
            branch = get_user_branch(request.user)
            if branch is not None:
                order.branch = branch
            order.save()
            formset.instance = order
            formset.save()
            assign_order_number(order)
            return redirect("journal:detail", pk=order.pk)
    else:
        form = _order_form(request)
        formset = OrderItemFormSet()
    return render(request, "journal/form.html", _order_context(request, form, formset))


@login_required
def update_view(request, pk):
    order = get_object_or_404(get_visible_orders(request.user), pk=pk)
    if request.method == "POST":
        form = _order_form(request, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order)
        if form.is_valid() and formset.is_valid():
            order = form.save()
            formset.save()
            assign_order_number(order)
            return redirect("journal:detail", pk=order.pk)
    else:
        form = _order_form(request, instance=order)
        formset = OrderItemFormSet(instance=order)
    return render(request, "journal/form.html", _order_context(request, form, formset, order=order))


@login_required
def detail_view(request, pk):
    order = get_object_or_404(get_visible_orders(request.user), pk=pk)
    return render(request, "journal/detail.html", {"order": order})


@login_required
def delete_view(request, pk):
    order = get_object_or_404(get_visible_orders(request.user), pk=pk)
    if request.method == "POST":
        order.delete()
        return redirect("journal:list")
    return render(request, "journal/confirm_delete.html", {"order": order})