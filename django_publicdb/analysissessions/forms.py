from django import forms
from models import *
from inforecords.models import *
from datetime import date

class SessionRequestForm(forms.Form):
   first_name = forms.CharField(max_length=50)
   sur_name = forms.CharField(max_length=50)
   email = forms.EmailField()
   school = forms.CharField(max_length=50)
   cluster = forms.ModelChoiceField(queryset=inforecords.Cluster.objects.all())
   start_date = forms.DateField()
 

