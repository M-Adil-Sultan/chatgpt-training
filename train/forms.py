from django import forms
from .models import Train_dataset

class TrainForm(forms.ModelForm):
    class Meta:
        model = Train_dataset
        fields = ['question', 'answers']
