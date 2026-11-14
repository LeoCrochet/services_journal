from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ServiceForm
from .models import Service


@login_required
def list_view(request):
    services = Service.objects.all()
    query = request.GET.get("q", "").strip()
    if query:
        services = services.filter(name__icontains=query)
    return render(request, "services/list.html", {"services": services, "query": query})


@login_required
def create_view(request):
    form = ServiceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("services:list")
    return render(request, "services/form.html", {"form": form, "title": "Новая услуга"})


@login_required
def update_view(request, pk):
    service = get_object_or_404(Service, pk=pk)
    form = ServiceForm(request.POST or None, instance=service)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("services:list")
    return render(request, "services/form.html", {"form": form, "title": "Редактировать услугу"})


@login_required
def delete_view(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == "POST":
        service.delete()
        return redirect("services:list")
    return render(request, "services/confirm_delete.html", {"service": service})