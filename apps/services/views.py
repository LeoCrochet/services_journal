from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import admin_required

from .forms import ServiceForm
from .models import Service


@login_required
def list_view(request):
    services = Service.objects.all()
    query = request.GET.get("q", "").strip()
    if query:
        services = services.filter(name__icontains=query)

    paginator = Paginator(services, 25)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "services/list.html",
        {"services": page_obj, "page_obj": page_obj, "query": query},
    )


@admin_required
def create_view(request):
    form = ServiceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("services:list")
    return render(request, "services/form.html", {"form": form, "title": "Новая услуга"})


@admin_required
def update_view(request, pk):
    service = get_object_or_404(Service, pk=pk)
    form = ServiceForm(request.POST or None, instance=service)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("services:list")
    return render(request, "services/form.html", {"form": form, "title": "Редактировать услугу"})


@admin_required
def delete_view(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == "POST":
        service.delete()
        return redirect("services:list")
    return render(request, "services/confirm_delete.html", {"service": service})