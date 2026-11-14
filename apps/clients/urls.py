from django.urls import path

from . import views

app_name = "clients"

urlpatterns = [
    path("", views.list_view, name="list"),
    path("create/", views.create_view, name="create"),
    path("<int:pk>/", views.detail_view, name="detail"),
    path("<int:pk>/edit/", views.update_view, name="update"),
    path("<int:pk>/delete/", views.delete_view, name="delete"),
]
