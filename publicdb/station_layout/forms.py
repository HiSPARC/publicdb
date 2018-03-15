from datetime import date

from django import forms

from ..inforecords.models import Station

todays_year = range(2004, date.today().year + 1)


class StationLayoutQuarantineForm(forms.Form):
    name = forms.CharField(max_length=50)
    email = forms.EmailField()

    station = forms.ModelChoiceField(
        queryset=Station.objects.filter(pc__is_test=False).distinct())
    active_date = forms.DateTimeField(
        help_text="Date the detectors were placed in this configuration, "
                  "e.g. '2010-5-17 12:45'.")

    # Master detectors
    detector_1_radius = forms.FloatField(min_value=-60, max_value=60)
    detector_1_alpha = forms.FloatField(min_value=-360, max_value=360)
    detector_1_height = forms.FloatField(min_value=-60, max_value=60,
                                         initial=0.)
    detector_1_beta = forms.FloatField(min_value=-360, max_value=360)
    detector_2_radius = forms.FloatField(min_value=-60, max_value=60)
    detector_2_alpha = forms.FloatField(min_value=-360, max_value=360)
    detector_2_height = forms.FloatField(min_value=-60, max_value=60,
                                         initial=0.)
    detector_2_beta = forms.FloatField(min_value=-360, max_value=360)

    # Optional slave detectors
    detector_3_radius = forms.FloatField(min_value=-60, max_value=60,
                                         required=False)
    detector_3_alpha = forms.FloatField(min_value=-360, max_value=360,
                                        required=False)
    detector_3_height = forms.FloatField(min_value=-60, max_value=60,
                                         initial=0., required=False)
    detector_3_beta = forms.FloatField(min_value=-360, max_value=360,
                                       required=False)
    detector_4_radius = forms.FloatField(min_value=-60, max_value=60,
                                         required=False)
    detector_4_alpha = forms.FloatField(min_value=-360, max_value=360,
                                        required=False)
    detector_4_height = forms.FloatField(min_value=-60, max_value=60,
                                         initial=0., required=False)
    detector_4_beta = forms.FloatField(min_value=-360, max_value=360,
                                       required=False)


class ReviewStationLayoutForm(forms.Form):
    approved = forms.BooleanField(required=False)
