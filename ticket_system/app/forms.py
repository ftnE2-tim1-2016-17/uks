from django import forms
from django.forms import ModelForm
from .models import Issue


class DateInput(forms.DateInput):
    input_type = 'date'

class TimeInput(forms.TimeInput):
    input_type = 'time'
