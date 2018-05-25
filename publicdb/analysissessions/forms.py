from datetime import date

from django import forms
from django.forms.extras.widgets import SelectDateWidget

from ..inforecords.models import Cluster

todays_year = list(range(2004, date.today().year + 1))


class SessionRequestForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    sur_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    school = forms.CharField(max_length=50)
    cluster = forms.ModelChoiceField(queryset=Cluster.objects.all())
    start_date = forms.DateField(widget=SelectDateWidget(years=todays_year))
    number_of_events = forms.IntegerField()
