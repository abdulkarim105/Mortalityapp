from django.urls import path
from . import views

app_name = "risk"

urlpatterns = [
    path("encounters/<int:encounter_id>/generate/", views.generate, name="generate"),
    path("assessments/<int:assessment_id>/", views.detail, name="detail"),
]
