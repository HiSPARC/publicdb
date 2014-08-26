from django import forms
from django_publicdb.inforecords.models import *
from datetime import date
from django.forms.extras.widgets import SelectDateWidget

todays_year = range(2004, int(date.today().strftime("%Y")) + 1)

class QuarantineForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    sur_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    station = forms.ModelChoiceField(queryset=Station.objects.all())
    scintillator_1_alpha = forms.FloatField(required=True)
    scintillator_1_beta = forms.FloatField()
    scintillator_1_radius = forms.FloatField(required=True)
    scintillator_1_height = forms.FloatField()
    scintillator_2_alpha = forms.FloatField(required=True)
    scintillator_2_beta = forms.FloatField()
    scintillator_2_radius = forms.FloatField(required=True)
    scintillator_2_height = forms.FloatField()
    scintillator_3_alpha = forms.FloatField(required=True)
    scintillator_3_beta = forms.FloatField()
    scintillator_3_radius = forms.FloatField(required=True)
    scintillator_3_height = forms.FloatField()
    scintillator_4_alpha = forms.FloatField(required=True)
    scintillator_4_beta = forms.FloatField()
    scintillator_4_radius = forms.FloatField(required=True)
    scintillator_4_height = forms.FloatField()
    active_date = forms.DateField(widget=SelectDateWidget(years=todays_year))