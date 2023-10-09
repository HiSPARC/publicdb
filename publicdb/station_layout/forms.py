from functools import partial

from django import forms

from ..inforecords.models import Station

# Distance and angle limits
DISTANCE_LIMITS = {'min_value': -60, 'max_value': 60}  # meters
ANGLE_LIMITS = {'min_value': -360, 'max_value': 360}  # degrees

radius_field = partial(forms.FloatField, **DISTANCE_LIMITS)
alpha_field = partial(forms.FloatField, **ANGLE_LIMITS)
height_field = partial(forms.FloatField, initial=0.0, **DISTANCE_LIMITS)
beta_field = partial(forms.FloatField, **ANGLE_LIMITS)


class StationLayoutQuarantineForm(forms.Form):
    name = forms.CharField(max_length=255)
    email = forms.EmailField()

    station = forms.ModelChoiceField(queryset=Station.objects.filter(pcs__is_test=False).distinct())
    active_date = forms.DateTimeField(
        help_text="Date the detectors were placed in this configuration, e.g. '2010-5-17 12:45'.",
    )

    # Master detectors
    detector_1_radius = radius_field()
    detector_1_alpha = alpha_field()
    detector_1_height = height_field()
    detector_1_beta = beta_field()
    detector_2_radius = radius_field()
    detector_2_alpha = alpha_field()
    detector_2_height = height_field()
    detector_2_beta = beta_field()

    # Optional secondary detectors
    detector_3_radius = radius_field(required=False)
    detector_3_alpha = alpha_field(required=False)
    detector_3_height = height_field(required=False)
    detector_3_beta = beta_field(required=False)
    detector_4_radius = radius_field(required=False)
    detector_4_alpha = alpha_field(required=False)
    detector_4_height = height_field(required=False)
    detector_4_beta = beta_field(required=False)


class ReviewStationLayoutForm(forms.Form):
    approved = forms.BooleanField(required=False)
