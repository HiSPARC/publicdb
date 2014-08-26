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
    scintillator_1_alpha = models.FloatField(null=True, blank=True)
    scintillator_1_beta = models.FloatField(null=True, blank=True)
    scintillator_1_radius = models.FloatField(null=True, blank=True)
    scintillator_1_height = models.FloatField(null=True, blank=True)
    scintillator_2_alpha = models.FloatField(null=True, blank=True)
    scintillator_2_beta = models.FloatField(null=True, blank=True)
    scintillator_2_radius = models.FloatField(null=True, blank=True)
    scintillator_2_height = models.FloatField(null=True, blank=True)
    if inforecords.Station.filter(name=station).number_of_detectors() == 4:
        scintillator_3_alpha = models.FloatField(null=True, blank=True)
        scintillator_3_beta = models.FloatField(null=True, blank=True)
        scintillator_3_radius = models.FloatField(null=True, blank=True)
        scintillator_3_height = models.FloatField(null=True, blank=True)
        scintillator_4_alpha = models.FloatField(null=True, blank=True)
        scintillator_4_beta = models.FloatField(null=True, blank=True)
        scintillator_4_radius = models.FloatField(null=True, blank=True)
        scintillator_4_height = models.FloatField(null=True, blank=True)
    active_date = forms.DateField(widget=SelectDateWidget(years=todays_year))