from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from core.views import handler404, handler500

handler404 = handler404
handler500 = handler500

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", include("dashboard.urls")),
    path("inventory/", include("inventory.urls")),
    path("health/", lambda r: HttpResponse("OK"), name="health"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
