# patients/urls.py
from django.urls import path
from . import views

app_name = "patients"

urlpatterns = [
    path("", views.patient_list, name="patient_list"),
    path("patients/new/", views.patient_create, name="patient_create"),
    path("patients/<int:patient_id>/", views.patient_detail, name="patient_detail"),
    path("patients/<int:patient_id>/delete/", views.patient_delete, name="patient_delete"),

    path("encounters/new/", views.encounter_create, name="encounter_create"),
    path("encounters/<int:encounter_id>/", views.encounter_detail, name="encounter_detail"),
]
