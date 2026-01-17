# observations/views.py

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from audit.utils import log_event
from patients.models import Encounter

from .forms import ObservationSetForm
from .models import ObservationSet

# ✅ import your feature engineering function
from .feature_engineering import engineer_features


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

            log_event(
                user=request.user,
                action="OBS_CREATED",
                obj=obs,
                details={"encounter_id": enc.id},
            )
            messages.success(request, "Observation set saved.")
            return redirect("patients:encounter_detail", encounter_id=enc.id)
    else:
        form = ObservationSetForm()

    return render(
        request,
        "observations/obs_form.html",
        {"form": form, "encounter": enc},
    )


@login_required
def obs_detail(request, obs_id: int):
    obs = get_object_or_404(ObservationSet, id=obs_id)
    features = [(c, getattr(obs, c)) for c in ObservationSet.feature_columns()]
    return render(request, "observations/obs_detail.html", {"obs": obs, "features": features})


# ✅ NEW: API endpoint for JSON upload → engineered features
@login_required
@permission_required("observations.add_observationset", raise_exception=True)
@require_POST
def engineer_features_api(request):
    """
    POST JSON -> returns {"status":"ok","features":{...}, "missing_features":[...]} etc.

    Accepts either:
      1) Raw ICU JSON (has admission_time + current_time + measurements) -> runs engineer_features()
      2) Already-engineered feature JSON -> echoes back (and reports missing keys)
    """
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse(
            {"status": "error", "message": "Invalid JSON payload"},
            status=400,
        )

    # Allow array with one object
    if isinstance(data, list) and len(data) == 1 and isinstance(data[0], dict):
        data = data[0]

    if not isinstance(data, dict):
        return JsonResponse(
            {"status": "error", "message": "JSON must be an object (dict)"},
            status=400,
        )

    # Detect "raw ICU JSON" format (your notebook format)
    is_raw = (
        "admission_time" in data
        and "current_time" in data
        and isinstance(data.get("measurements"), list)
    )

    expected = list(ObservationSet.feature_columns())

    if is_raw:
        result = engineer_features(data)

        if not result.get("success"):
            return JsonResponse(
                {
                    "status": "error",
                    "message": result.get("error", "Feature engineering failed"),
                    "details": result.get("details"),
                },
                status=400,
            )

        # ✅ Always normalize + compute missing/unknown here
        features = result.get("features", {}) or {}

        missing = [k for k in expected if features.get(k) in (None, "")]
        unknown = [k for k in features.keys() if k not in expected]

        return JsonResponse(
            {
                "status": "ok",
                "features": {k: features.get(k) for k in expected},  # return only expected keys
                "missing_features": missing if missing else None,
                "imputed_features": result.get("imputed_features") or None,
                "unknown_keys": unknown if unknown else None,
                "validation_message": result.get("validation_message"),
            }
        )

    # Otherwise treat as already-feature JSON and just check missing keys
    features = data

    missing = [k for k in expected if features.get(k) in (None, "")]
    unknown = [k for k in features.keys() if k not in expected]

    return JsonResponse(
        {
            "status": "ok",
            "features": {k: features.get(k) for k in expected},  # only return expected keys
            "missing_features": missing if missing else None,
            "unknown_keys": unknown if unknown else None,
            "validation_message": "Feature JSON loaded.",
        }
    )
