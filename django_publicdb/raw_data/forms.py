from django import forms

from ..inforecords.models import Station, Cluster


TYPES = [('events', 'Events'),
         ('weather', 'Weather'),
         ('lightning', ' Lightning')]  # added for lightning
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
    data_type = forms.ChoiceField(choices=TYPES, widget=forms.RadioSelect())
    station_events = forms.ModelChoiceField(
        Station.objects.filter(summary__num_events__isnull=False).distinct(),
        empty_label='---------', required=False)
    station_weather = forms.ModelChoiceField(
        Station.objects.filter(summary__num_weather__isnull=False).distinct(),
        empty_label='---------', required=False)
    lightning_type = forms.ChoiceField(choices=LGT_TYPES, initial=4,
                                       required=False)
    start = forms.DateTimeField(help_text="e.g. '2013-5-17', or "
                                          "'2013-5-17 12:45'")
    end = forms.DateTimeField(help_text="e.g. '2013-5-18', or "
                                        "'2013-5-18 9:05'")
    download = forms.BooleanField(required=False)

    def clean(self):
        """Check the choices to ensure the combination of choices are valid"""

        cleaned_data = super(DataDownloadForm, self).clean()
        data_type = cleaned_data.get('data_type')
        if data_type == 'events':
            del cleaned_data["station_weather"]
            del cleaned_data["lightning_type"]
            station = cleaned_data.get('station_events')
            if not station:
                self._errors["station_events"] = \
                    self.error_class([u'Choose a station'])
                del cleaned_data["station_events"]
            else:
                cleaned_data["station"] = station
        elif data_type == 'weather':
            del cleaned_data["station_events"]
            del cleaned_data["lightning_type"]
            station = cleaned_data.get('station_weather')
            if not station:
                self._errors["station_weather"] = \
                    self.error_class([u'Choose a station'])
                del cleaned_data["station_weather"]
            else:
                cleaned_data["station"] = station
        elif data_type == 'lightning':
            del cleaned_data["station_events"]
            del cleaned_data["station_weather"]
        return cleaned_data


class CoincidenceDownloadForm(forms.Form):
    filter_by = forms.ChoiceField(choices=FILTER, widget=forms.RadioSelect())
    cluster = forms.ModelChoiceField(Cluster.objects.filter(parent=None),
                                     empty_label='---------',
                                     required=False)
    stations = forms.CharField(help_text="e.g. '103, 104, 105'",
                               required=False)
    start = forms.DateTimeField(help_text="e.g. '2014-4-5', or "
                                          "'2014-4-18 12:45'")
    end = forms.DateTimeField(help_text="e.g. '2014-4-29', or "
                                        "'2014-04-30 9:05'")
    n = forms.IntegerField(min_value=2, help_text="Minimum number of events "
                                                  "in a coincidence")
    download = forms.BooleanField(required=False)

    def clean(self):
        """Check the choices to ensure the combination of choices are valid"""

        cleaned_data = super(CoincidenceDownloadForm, self).clean()
        filter_by = cleaned_data.get('filter_by')
        if filter_by == 'network':
            del cleaned_data["cluster"]
            del cleaned_data["stations"]
            return cleaned_data
        elif filter_by == 'cluster':
            del cleaned_data["stations"]
            cluster = cleaned_data.get('cluster')
            if not cluster:
                self._errors["cluster"] = \
                    self.error_class([u'Choose a cluster'])
                del cleaned_data["cluster"]
        elif filter_by == 'stations':
            del cleaned_data["cluster"]
            stations = cleaned_data.get('stations')
            if not stations:
                self._errors["stations"] = \
                    self.error_class([u'A list of stations is required'])
            else:
                try:
                    s_numbers = [int(x)
                                 for x in stations.strip('[]').split(',')]
                except:
                    self._errors["stations"] = \
                        self.error_class([u'Incorrect station entry'])
                    del cleaned_data["stations"]
                    return cleaned_data
                if len(s_numbers) < cleaned_data.get('n'):
                    self._errors["stations"] = \
                        self.error_class([u'Enter at least N stations.'])
                    del cleaned_data["stations"]
                    return cleaned_data
                if len(s_numbers) > 30:
                    self._errors["stations"] = \
                        self.error_class([u'Exceeded limit of 30 stations.'])
                    del cleaned_data["stations"]
                    return cleaned_data
                if not (Station.objects.filter(number__in=s_numbers).count() ==
                        len(s_numbers)):
                    self._errors["stations"] = \
                        self.error_class([u'Invalid station numbers.'])
                    del cleaned_data["stations"]
                    return cleaned_data
        return cleaned_data
