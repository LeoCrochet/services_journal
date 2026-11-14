from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("order/<int:pk>/pdf/", views.order_pdf, name="order_pdf"),
    path("order/<int:pk>/docx/", views.order_docx, name="order_docx"),
    path("clients/excel/", views.clients_excel, name="clients_excel"),
    path("services/excel/", views.services_excel, name="services_excel"),
    path("orders/excel/", views.orders_excel, name="orders_excel"),
    path("", views.report_index, name="report_index"),
    path("pdf/", views.report_pdf, name="report_pdf"),
]