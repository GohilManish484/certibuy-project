from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

handler403 = 'core.error_handlers.handler403'
handler404 = 'core.error_handlers.handler404'
handler500 = 'core.error_handlers.handler500'

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("accounts/", include("accounts.urls")),
    path("products/", include("products.urls")),
    path("sellers/", include("sellers.urls")),
    path("inspections/", include("inspections.urls")),
    path("orders/", include("orders.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
