from datetime import date

from django import forms

from ..inforecords.models import Cluster

todays_year = list(range(2004, date.today().year + 1))


class SessionRequestForm(forms.Form):
    first_name = forms.CharField(max_length=255)
    sur_name = forms.CharField(max_length=255)
    email = forms.EmailField()
    school = forms.CharField(max_length=255)
    cluster = forms.ModelChoiceField(queryset=Cluster.objects.all())
    start_date = forms.DateField(widget=forms.SelectDateWidget(years=todays_year))
    number_of_events = forms.IntegerField()
