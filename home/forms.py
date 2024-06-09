from django import forms
from.models import *
from django.utils import timezone
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class TaskForm(forms.ModelForm ):
    class Meta:
        model=Task
        fields='__all__'
    def clean(self):
        data = self.cleaned_data['comletiondate']
        if data < timezone.now():
            raise forms.ValidationError({"comletiondate": "La fecha no puede ser menor a la actual"})
        # return data 
        