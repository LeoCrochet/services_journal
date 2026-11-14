from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.services.models import Service

from .forms import OrderForm, OrderItemFormSet
from .models import Order


@login_required
def list_view(request):
    query = request.GET.get("q", "").strip()
    orders = Order.objects.select_related("client")
    if query:
        orders = orders.filter(client__fio__icontains=query)
    return render(request, "journal/list.html", {"orders": orders, "query": query})


def _services_data():
    return list(Service.objects.values("id", "name", "description", "price"))


@login_required
def create_view(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            order = form.save()
            formset.instance = order
            formset.save()
            return redirect("journal:detail", pk=order.pk)
    else:
        form = OrderForm()
        formset = OrderItemFormSet()
    return render(
        request,
        "journal/form.html",
        {"form": form, "formset": formset, "services_data": _services_data()},
    )


@login_required
def update_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect("journal:detail", pk=order.pk)
    else:
        form = OrderForm(instance=order)
        formset = OrderItemFormSet(instance=order)
    return render(
        request,
        "journal/form.html",
        {"form": form, "formset": formset, "services_data": _services_data(), "order": order},
    )


@login_required
def detail_view(request, pk):
    order = get_object_or_404(Order.objects.select_related("client"), pk=pk)
    return render(request, "journal/detail.html", {"order": order})


@login_required
def delete_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        order.delete()
        return redirect("journal:list")
    return render(request, "journal/confirm_delete.html", {"order": order})