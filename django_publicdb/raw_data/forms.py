from django import forms

from django_publicdb.inforecords.models import Station, Cluster


TYPES = [('events','Events'),
         ('weather','Weather')]


class DataDownloadForm(forms.Form):
    station = forms.ModelChoiceField(Station.objects.all())
    start = forms.DateTimeField(help_text="e.g. '2013-5-17', or "
                                          "'2013-5-17 12:45'")
    end = forms.DateTimeField(help_text="e.g. '2013-5-18', or "
                                        "'2013-5-18 9:05'")
    data_type = forms.ChoiceField(choices=TYPES, widget=forms.RadioSelect())
    download = forms.BooleanField(required=False)


class CoincidenceDownloadForm(forms.Form):
    cluster = forms.ModelChoiceField(Cluster.objects.filter(parent=None),
                                     empty_label='All clusters',
                                     required=False)
    start = forms.DateTimeField(help_text="e.g. '2014-4-5', or "
                                          "'2014-4-18 12:45'")
    end = forms.DateTimeField(help_text="e.g. '2014-4-29', or "
                                        "'2014-04-30 9:05'")
    n = forms.IntegerField(min_value=2, help_text="Minimum number of events "
                                                  "in a coincidence")
    download = forms.BooleanField(required=False)
