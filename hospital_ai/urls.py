from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", include(("patients.urls", "patients"), namespace="patients")),
    path("", include(("observations.urls", "observations"), namespace="observations")),
    path("risk/", include(("risk.urls", "risk"), namespace="risk")),
]
