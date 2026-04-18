from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", include("dashboard.urls")),
    path("inventory/", include("inventory.urls")),
    path("health/", lambda r: HttpResponse("OK"), name="health"),
]
