from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("apps.accounts.urls")),
    path("clients/", include("apps.clients.urls")),
    path("services/", include("apps.services.urls")),
    path("journal/", include("apps.journal.urls")),
    path("reports/", include("apps.reports.urls")),
]