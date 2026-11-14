from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("order/<int:pk>/pdf/", views.order_pdf, name="order_pdf"),
]