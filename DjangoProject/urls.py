from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("pages.urls")),                      # homepage
    path("", include(("catalog.urls", "catalog"), namespace="catalog")),  # k/… a p/…
]
