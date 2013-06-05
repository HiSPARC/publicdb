from django import forms

from django_publicdb.inforecords.models import Station

class DataDownloadForm(forms.Form):
    station = forms.ModelChoiceField(Station.objects.all())
    start = forms.DateTimeField(help_text="e.g. '2013-5-17', or "
                                          "'2013-5-17 12:45'")
    end = forms.DateTimeField(help_text="e.g. '2013-5-18', or "
                                        "'2013-5-18 9:05'")
    download = forms.BooleanField(required=False)
