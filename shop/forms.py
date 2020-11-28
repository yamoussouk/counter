from django import forms
from django.forms import ModelForm

from .models import Message


class ContactForm(ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'email', 'message']
        widgets = dict(subject=forms.HiddenInput, email=forms.HiddenInput, message=forms.HiddenInput)
