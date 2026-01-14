
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render

from patients.models import Encounter
from .models import ObservationSet
from .forms import ObservationSetForm
from audit.utils import log_event

@login_required
@permission_required("observations.add_observationset", raise_exception=True)
def obs_create(request, encounter_id: int):
    enc = get_object_or_404(Encounter, id=encounter_id)

    if request.method == "POST":
        form = ObservationSetForm(request.POST)
        if form.is_valid():
            obs = form.save(commit=False)
            obs.encounter = enc
            obs.recorded_by = request.user
            obs.save()
            log_event(user=request.user, action="OBS_CREATED", obj=obs, details={"encounter_id": enc.id})
            messages.success(request, "Observation set saved.")
            return redirect("patients:encounter_detail", encounter_id=enc.id)
    else:
        form = ObservationSetForm()

    return render(request, "observations/obs_form.html", {"form": form, "encounter": enc})

@login_required
def obs_detail(request, obs_id: int):
    obs = get_object_or_404(ObservationSet, id=obs_id)
    features = [(c, getattr(obs, c)) for c in ObservationSet.feature_columns()]
    return render(request, "observations/obs_detail.html", {"obs": obs, "features": features})
