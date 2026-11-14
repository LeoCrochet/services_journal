from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.services import get_user_branch

from .forms import ClientForm
from .services import get_visible_clients


@login_required
def list_view(request):
    query = request.GET.get("q", "").strip()
    clients = get_visible_clients(request.user)
    if query:
        clients = clients.filter(fio__icontains=query)
    return render(request, "clients/list.html", {"clients": clients, "query": query})


def _client_form(request, instance=None):
    data = request.POST or None
    form = ClientForm(data, instance=instance)
    # Оператору подставляем его площадку автоматически
    branch = get_user_branch(request.user)
    if branch is not None:
        form.fields["branch"].queryset = form.fields["branch"].queryset.filter(pk=branch.pk)
        form.fields["branch"].initial = branch
    return form


@login_required
def create_view(request):
    form = _client_form(request)
    if request.method == "POST":
        branch = get_user_branch(request.user)
        if branch is not None:
            form.data = form.data.copy()
            form.data["branch"] = str(branch.pk)
        if form.is_valid():
            form.save()
            return redirect("clients:list")
    return render(request, "clients/form.html", {"form": form, "title": "Новый клиент"})


@login_required
def update_view(request, pk):
    client = get_object_or_404(get_visible_clients(request.user), pk=pk)
    form = _client_form(request, instance=client)
    if request.method == "POST":
        branch = get_user_branch(request.user)
        if branch is not None:
            form.data = form.data.copy()
            form.data["branch"] = str(branch.pk)
        if form.is_valid():
            form.save()
            return redirect("clients:list")
    return render(request, "clients/form.html", {"form": form, "title": "Редактировать клиента"})


@login_required
def delete_view(request, pk):
    client = get_object_or_404(get_visible_clients(request.user), pk=pk)
    if request.method == "POST":
        client.delete()
        return redirect("clients:list")
    return render(request, "clients/confirm_delete.html", {"client": client})