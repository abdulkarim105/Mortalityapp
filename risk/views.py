from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render

from patients.models import Encounter
from observations.models import ObservationSet
from .models import RiskAssessment
from .forms import GenerateRiskForm, RiskCommentForm
from .services import predict_180d_mortality, risk_band_for_probability
from .driver_logic import build_clinical_drivers


@login_required
@permission_required("risk.add_riskassessment", raise_exception=True)
def generate(request, encounter_id):
    encounter = get_object_or_404(Encounter, id=encounter_id)

    latest_obs = ObservationSet.objects.filter(
        encounter=encounter
    ).order_by("-recorded_at").first()

    if not latest_obs:
        messages.error(request, "No observations found. Enter vitals/labs first.")
        return redirect("patients:encounter_detail", encounter.id)

    if request.method == "POST":
        form = GenerateRiskForm(request.POST)
        if form.is_valid():
            prob = predict_180d_mortality(latest_obs)
            band = risk_band_for_probability(prob)

            ra = RiskAssessment.objects.create(
                encounter=encounter,
                observation_set=latest_obs,
                risk_180d=prob * 100,
                risk_band=band,
                model_version=settings.ML_MODEL_VERSION,
                created_by=request.user,
                doctor_name=form.cleaned_data["doctor_name"],  # ✅ typed value
                doctor_comment=""
            )

            messages.success(request, "Risk prediction generated.")
            return redirect("risk:detail", ra.id)
    else:
        form = GenerateRiskForm()

    return render(request, "risk/generate.html", {
        "encounter": encounter,
        "form": form,
    })


@login_required
def detail(request, assessment_id):
    ra = get_object_or_404(RiskAssessment, id=assessment_id)

    # Save doctor comment
    if request.method == "POST":
        form = RiskCommentForm(request.POST)
        if form.is_valid():
            ra.doctor_comment = form.cleaned_data["doctor_comment"]
            ra.save(update_fields=["doctor_comment"])
            messages.success(request, "Doctor comment saved.")
            return redirect("risk:detail", ra.id)
    else:
        form = RiskCommentForm(initial={"doctor_comment": ra.doctor_comment})

    show_all = request.GET.get("all") == "1"
    drivers, shown_count, high_count, total_abnormal = build_clinical_drivers(
        ra.observation_set, show_all=show_all
    )

    features = [(c, getattr(ra.observation_set, c)) for c in ObservationSet.feature_columns()]

    return render(request, "risk/detail.html", {
        "ra": ra,
        "drivers": drivers,
        "shown_count": shown_count,
        "high_count": high_count,
        "total_abnormal": total_abnormal,
        "show_all": show_all,
        "features": features,
        "comment_form": form,
    })
