from django import forms
from django.forms import fields
from django.forms.models import model_to_dict
from .models import ReviewRating

class  ReviewForm(forms.ModelForm):
    class Meta:
        model=ReviewRating
        fields=['subject','review','rating']