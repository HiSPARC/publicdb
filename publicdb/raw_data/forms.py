from django import forms
from django.core.exceptions import ValidationError

from ..inforecords.models import Cluster, Station

TYPES = [('events', 'Events'),
         ('weather', 'Weather'),
         ('lightning', 'Lightning'),
         ('singles', 'Singles')]

LGT_TYPES = [('0', 'Single-point'),
             ('1', 'Cloud-cloud'),
             ('2', 'Cloud-cloud mid'),
             ('3', 'Cloud-cloud end'),
             ('4', 'Cloud-ground'),
             ('5', 'Cloud-ground return')]

FILTER = [('network', 'Network'),
          ('cluster', 'Cluster'),
          ('stations', 'Stations')]


class DataDownloadForm(forms.Form):
    agree = forms.BooleanField(
        label='I have read and agree to the terms and conditions above',
        initial=False,
        required=True
    )

    data_type = forms.ChoiceField(choices=TYPES, widget=forms.RadioSelect())
    station_events = forms.ModelChoiceField(
        Station.objects.filter(summaries__num_events__isnull=False).distinct(),
        empty_label='---------', required=False)
    station_weather = forms.ModelChoiceField(
        Station.objects.filter(summaries__num_weather__isnull=False).distinct(),
        empty_label='---------', required=False)
    lightning_type = forms.ChoiceField(choices=LGT_TYPES, initial=4, required=False)
    station_singles = forms.ModelChoiceField(
        Station.objects.filter(summaries__num_singles__isnull=False).distinct(),
        empty_label='---------', required=False)
    start = forms.DateTimeField(help_text="e.g. '2013-5-17', or '2013-5-17 12:45'")
    end = forms.DateTimeField(help_text="e.g. '2013-5-18', or '2013-5-18 9:05'")
    download = forms.BooleanField(initial=True, required=False)

    def clean(self):
        """Check the choices to ensure the combination of choices are valid"""

        cleaned_data = super(DataDownloadForm, self).clean()
        data_type = cleaned_data.get('data_type')

        for station_data_type in ['events', 'weather', 'singles']:
            station_field = 'station_{}'.format(station_data_type)
            if data_type == station_data_type:
                station = cleaned_data.get(station_field)
                if not station:
                    self.add_error(station_field, u'Choose a station')
                else:
                    cleaned_data["station"] = station
            else:
                del cleaned_data[station_field]
        return cleaned_data


class CoincidenceDownloadForm(forms.Form):
    agree = forms.BooleanField(
        label='I have read and agree to the terms and conditions above',
        initial=False,
        required=True
    )

    filter_by = forms.ChoiceField(choices=FILTER, widget=forms.RadioSelect())
    cluster = forms.ModelChoiceField(Cluster.objects.filter(parent=None),
                                     empty_label='---------',
                                     required=False)
    stations = forms.CharField(help_text="e.g. '103, 104, 105'", required=False)
    start = forms.DateTimeField(help_text="e.g. '2014-4-5', or '2014-4-18 12:45'")
    end = forms.DateTimeField(help_text="e.g. '2014-4-29', or '2014-04-30 9:05'")
    n = forms.IntegerField(min_value=2, help_text="Minimum number of events in a coincidence")
    download = forms.BooleanField(initial=True, required=False)

    def clean(self):
        """Check the choices to ensure the combination of choices are valid"""

        cleaned_data = super(CoincidenceDownloadForm, self).clean()
        filter_by = cleaned_data.get('filter_by')
        if filter_by == 'network':
            del cleaned_data["cluster"]
            del cleaned_data["stations"]
        elif filter_by == 'cluster':
            del cleaned_data["stations"]
            cluster = cleaned_data.get('cluster')
            if not cluster:
                self.add_error("cluster", ValidationError(u'Choose a cluster.', 'invalid_choice'))
        elif filter_by == 'stations':
            del cleaned_data["cluster"]
            msg = None
            stations = cleaned_data.get('stations')
            if not stations:
                msg = ValidationError(u'A list of stations is required.', 'required')
            else:
                try:
                    s_numbers = [int(x) for x in stations.strip('[]()').split(',')]
                except Exception:
                    msg = ValidationError(u'Incorrect station entry.', 'incorrect_entry')
                else:
                    if len(s_numbers) < cleaned_data.get('n'):
                        msg = ValidationError(u'Enter at least N stations.', 'too_few')
                    elif len(s_numbers) > 30:
                        msg = ValidationError(u'Exceeded limit of 30 stations.', 'too_many')
                    elif not Station.objects.filter(number__in=s_numbers).count() == len(s_numbers):
                        msg = ValidationError(u'Invalid station numbers.', 'invalid_choices')
            if msg is not None:
                self.add_error('stations', msg)

        return cleaned_data
