from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .decorators import admin_required
from .forms import BranchForm, UserForm
from .models import Branch


@login_required
def home(request):
    return redirect("journal:list")


@admin_required
def branch_list(request):
    branches = Branch.objects.all()
    return render(request, "accounts/branch_list.html", {"branches": branches})


@admin_required
def branch_create(request):
    form = BranchForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("accounts:branch_list")
    return render(request, "accounts/branch_form.html", {"form": form, "title": "Новая площадка"})


@admin_required
def branch_update(request, pk):
    branch = get_object_or_404(Branch, pk=pk)
    form = BranchForm(request.POST or None, instance=branch)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("accounts:branch_list")
    return render(request, "accounts/branch_form.html", {"form": form, "title": "Редактировать площадку"})


@admin_required
def user_list(request):
    users = User.objects.select_related("profile__branch").order_by("username")
    return render(request, "accounts/user_list.html", {"users": users})


@admin_required
def user_create(request):
    form = UserForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("accounts:user_list")
    return render(request, "accounts/user_form.html", {"form": form, "title": "Новый пользователь"})


@admin_required
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    # Суперпользователя не редактируем через эту форму
    if user.is_superuser:
        return redirect("accounts:user_list")

    form = UserForm(request.POST or None, instance=user)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("accounts:user_list")
    return render(request, "accounts/user_form.html", {"form": form, "title": "Редактировать пользователя"})