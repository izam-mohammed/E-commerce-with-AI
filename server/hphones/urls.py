"""
URL configuration for hphones project.

"""
from django.contrib import admin
from django.urls import path, include
from hps.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("hps.urls")),
    path("", include("hps_adm.urls")),
    path("jet/", include("jet.urls", "jet")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
