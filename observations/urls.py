from django.urls import path
from . import views

app_name = "observations"

urlpatterns = [
    path("encounters/<int:encounter_id>/observations/new/", views.obs_create, name="obs_create"),
    path("observations/<int:obs_id>/", views.obs_detail, name="obs_detail"),
]
