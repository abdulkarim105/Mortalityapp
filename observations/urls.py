from django.urls import path
from . import views

app_name = "observations"

urlpatterns = [
    # existing URLs
    path("encounters/<int:encounter_id>/observations/new/", views.obs_create, name="obs_create"),
    path("observations/<int:obs_id>/", views.obs_detail, name="obs_detail"),

    # 🔹 NEW: API endpoint for JSON upload → feature extraction
    path("engineer-features/", views.engineer_features_api, name="engineer_features_api"),
]
