from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ClientForm
from .models import Client


@login_required
def list_view(request):
    query = request.GET.get("q", "").strip()
    clients = Client.objects.all()
    if query:
        clients = clients.filter(fio__icontains=query)
    return render(request, "clients/list.html", {"clients": clients, "query": query})


@login_required
def create_view(request):
    form = ClientForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("clients:list")
    return render(request, "clients/form.html", {"form": form, "title": "Новый клиент"})


@login_required
def update_view(request, pk):
    client = get_object_or_404(Client, pk=pk)
    form = ClientForm(request.POST or None, instance=client)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("clients:list")
    return render(request, "clients/form.html", {"form": form, "title": "Редактировать клиента"})


@login_required
def delete_view(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        client.delete()
        return redirect("clients:list")
    return render(request, "clients/confirm_delete.html", {"client": client})