import django.core.validators
from django import forms


class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(validators=[django.core.validators.MinValueValidator(0)], initial=1)
    color = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    stud = forms.CharField(widget=forms.HiddenInput)
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)


class CartAddGiftCardProductForm(forms.Form):
    amount = forms.IntegerField(required=True, initial=5000, widget=forms.HiddenInput)
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)


class CartDeliveryInfoForm(forms.Form):
    fullname = forms.CharField(required=True, widget=forms.HiddenInput)
    email = forms.EmailField(required=True, widget=forms.HiddenInput)
    firstname = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    lastname = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    fox_post = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    delivery_name = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    address = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    postal_code = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    city = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    note = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    delivery_type = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    phone = forms.CharField(required=True, widget=forms.HiddenInput, initial='')
    csomagkuldo = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
