from django import forms
from .models import Worker

class WorkersForm (forms.ModelForm):
    class Meta:
        model = Worker
        fields = ('name', 'reported_hash_rate', 'last_submit_time')