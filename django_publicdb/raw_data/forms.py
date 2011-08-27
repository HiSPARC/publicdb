from django import forms

from django_publicdb.inforecords import models as inforecords

class DataDownloadForm(forms.Form):
    station = forms.ModelChoiceField(queryset=inforecords.Station.objects.all())
    start_date = forms.DateField()
    end_date = forms.DateField()
