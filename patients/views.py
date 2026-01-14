from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .models import Patient, Encounter
from .forms import PatientForm, EncounterForm
from observations.models import ObservationSet
from risk.models import RiskAssessment


@login_required
def patient_list(request):
    q = request.GET.get("q", "").strip()

    patients = Patient.objects.all().order_by("full_name")

    if q:
        patients = patients.filter(
            Q(mrn__icontains=q) |
            Q(full_name__icontains=q)
        )

    return render(request, "patients/patient_list.html", {
        "patients": patients,
        "q": q,
    })


@login_required
@permission_required("patients.add_patient", raise_exception=True)
def patient_create(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            messages.success(request, "Patient created.")
            return redirect("patients:patient_detail", patient_id=patient.id)
    else:
        form = PatientForm()
    return render(request, "patients/patient_form.html", {"form": form, "title": "New patient"})


@login_required
def patient_detail(request, patient_id: int):
    patient = get_object_or_404(Patient, id=patient_id)
    encounters = patient.encounters.order_by("-admitted_at")
    return render(request, "patients/patient_detail.html", {"patient": patient, "encounters": encounters})


@login_required
@permission_required("patients.delete_patient", raise_exception=True)
@require_http_methods(["GET", "POST"])
def patient_delete(request, patient_id: int):
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == "POST":
        password = request.POST.get("password", "").strip()

        # Check current logged-in user's password
        user = authenticate(
            request,
            username=request.user.get_username(),
            password=password
        )

        if user is None:
            messages.error(request, "Incorrect password. Patient was NOT deleted.")
            return render(request, "patients/patient_confirm_delete.html", {"patient": patient})

        # Password correct -> delete patient
        patient.delete()
        messages.success(request, "Patient deleted.")
        return redirect("patients:patient_list")

    # GET -> show confirm page with password field
    return render(request, "patients/patient_confirm_delete.html", {"patient": patient})


@login_required
@permission_required("patients.add_encounter", raise_exception=True)
def encounter_create(request):
    if request.method == "POST":
        form = EncounterForm(request.POST)
        if form.is_valid():
            enc = form.save()
            messages.success(request, "Encounter created.")
            return redirect("patients:encounter_detail", encounter_id=enc.id)
    else:
        form = EncounterForm()
    return render(request, "patients/encounter_form.html", {"form": form, "title": "New encounter"})


@login_required
def encounter_detail(request, encounter_id: int):
    enc = get_object_or_404(Encounter, id=encounter_id)
    obs_list = ObservationSet.objects.filter(encounter=enc).order_by("-recorded_at")
    risk_list = RiskAssessment.objects.filter(encounter=enc).order_by("-created_at")
    latest_obs = obs_list.first()
    latest_risk = risk_list.first()
    return render(request, "patients/encounter_detail.html", {
        "encounter": enc,
        "obs_list": obs_list,
        "risk_list": risk_list,
        "latest_obs": latest_obs,
        "latest_risk": latest_risk,
    })
