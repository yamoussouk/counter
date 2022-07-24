import django.core.validators
from django import forms


class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(validators=[django.core.validators.MinValueValidator(0)], initial=1)
    color = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    stud = forms.CharField(required=False, widget=forms.HiddenInput)
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)


class CartAddCustomProductForm(forms.Form):
    quantity = forms.IntegerField(validators=[django.core.validators.MinValueValidator(0)], initial=1)
    color = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    stud = forms.CharField(widget=forms.HiddenInput)
    first_initial = forms.CharField(widget=forms.HiddenInput, max_length=2)
    second_initial = forms.CharField(widget=forms.HiddenInput, max_length=2)
    custom_date = forms.CharField(widget=forms.HiddenInput)
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)


class CartAddGiftCardProductForm(forms.Form):
    amount = forms.IntegerField(required=True, initial=5000, widget=forms.HiddenInput)
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)


class CartDeliveryInfoForm(forms.Form):
    full_name = forms.CharField(required=True, initial='Telek Elek')
    email = forms.EmailField(required=True, initial='tamas.kakuszi@gmail.com')
    phone = forms.CharField(required=True, initial='+36307138606', widget=forms.TextInput(
        attrs={'placeholder': '+36301231234',
               'title': 'Az elfogadott formátum a következő: +36301231234',
               'pattern': '[+][0-9]{1,3}[0-9]{6,}'}))
    billing_address = forms.CharField(required=True, initial='Telek utca', widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    billing_address_number = forms.CharField(required=True, initial='23')
    billing_postal_code = forms.CharField(required=True, initial='1111', widget=forms.TextInput(
        attrs={'title': 'Kérem, adjon meg egy négyjegyű irányítószámot!',
               'pattern': '[0-9]{4}'}))
    billing_city = forms.CharField(required=True, initial='Szeged', widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    delivery_type_code = forms.CharField(required=True, widget=forms.HiddenInput, initial='0')
    first_name = forms.CharField(required=False, initial='', widget=forms.TextInput(
        attrs={'class': 'form-control non-foxpost non-csomagkuldo non-delivery personal non-delivery',
               'placeholder': 'Vezetéknév'}))
    last_name = forms.CharField(required=False, initial='', widget=forms.TextInput(
        attrs={'class': 'non-foxpost non-csomagkuldo non-delivery personal non-delivery', 'placeholder': 'Keresztnév'}))
    fox_post = forms.CharField(required=False, initial='',
                               widget=forms.HiddenInput(
                                   attrs={'class': 'non-csomagkuldo non-delivery non-personal non-delivery'}))
    delivery_name = forms.CharField(required=False, initial='', widget=forms.TextInput(
        attrs={'class': 'form-control non-foxpost non-csomagkuldo non-personal'}))
    address = forms.CharField(required=False, initial='', widget=forms.TextInput(
        attrs={'class': 'form-control non-foxpost non-csomagkuldo non-personal'}))
    address_number = forms.CharField(required=False, initial='', widget=forms.TextInput(
        attrs={'class': 'form-control non-foxpost non-csomagkuldo non-personal'}))
    postal_code = forms.CharField(required=False, initial='', widget=forms.TextInput(
        attrs={'class': 'form-control non-foxpost non-csomagkuldo non-personal',
               'title': 'Kérem, adjon meg egy négyjegyű irányítószámot!',
               'pattern': '[0-9]{4}'}))
    city = forms.CharField(required=False, initial='', widget=forms.TextInput(
        attrs={'class': 'form-control non-foxpost non-csomagkuldo non-personal'}))
    note = forms.CharField(required=False, initial='', widget=forms.Textarea(
        attrs={'class': 'form-control non-foxpost non-csomagkuldo non-personal', "maxlength": "200", "rows": "4"}))
    csomagkuldo = forms.CharField(required=False, initial='',
                                  widget=forms.HiddenInput(
                                      attrs={'class': 'non-foxpost non-delivery non-personal non-delivery'}))
    product_note = forms.CharField(required=False, initial='', widget=forms.Textarea(
        attrs={'class': 'form-control', "maxlength": "200", "rows": "4"}))
