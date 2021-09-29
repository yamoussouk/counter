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
    fullname = forms.CharField(required=True, widget=forms.HiddenInput)
    email = forms.EmailField(required=True, widget=forms.HiddenInput)
    phone = forms.CharField(required=True, widget=forms.HiddenInput, initial='')
    billing_address = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    billing_postal_code = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    billing_city = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    firstname = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    lastname = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    fox_post = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    delivery_name = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    address = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    postal_code = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    city = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    note = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    delivery_type = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    csomagkuldo = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    product_note = forms.CharField(required=False, widget=forms.HiddenInput, initial='')


class CartDeliveryInfoFormNotHidden(forms.Form):
    full_name = forms.CharField(required=True, label='Teljes név*',
                               widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'full_name'}))
    phone = forms.CharField(required=True, initial='', label='Telefonszám*',
                            widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'phone_number'}))
    email = forms.EmailField(required=True, label='E-mail cím*',
                             widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'email_address'}))
    billing_address = forms.CharField(required=True, initial='', label='Utca, házszám*',
                                      widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'billing_address'}))
    billing_postal_code = forms.CharField(required=True, initial='', label='Irányítószám*', widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'billing_postal_code'}))
    billing_city = forms.CharField(required=True, initial='', label='Település*',
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'billing_city'}))
    product_note = forms.CharField(required=False, initial='', label='Megjegyzés',
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'product_note'}))
    first_name = forms.CharField(required=True, initial='', widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'first_name', 'placeholder': 'Vezetéknév'}))
    last_name = forms.CharField(required=True, initial='', widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'last_name', 'placeholder': 'Keresztnév'}))
    csomagkuldo = forms.CharField(required=False, initial='', widget=forms.HiddenInput)
    fox_post = forms.CharField(required=False, initial='', widget=forms.HiddenInput)
    delivery_name = forms.CharField(required=False, initial='', label='Név*',
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'delivery_full_name'}))
    address = forms.CharField(required=False, initial='', label='Utca, házszám*',
                              widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'd_address'}))
    postal_code = forms.CharField(required=False, initial='', label='Irányítószám*',
                                  widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'd_zip'}))
    city = forms.CharField(required=False, initial='', label='Település*',
                           widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'd_city'}))
    note = forms.CharField(required=False, initial='', label='Egyéb Információk',
                           widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'd_note'}))
    delivery_type = forms.CharField(required=False, initial='', widget=forms.HiddenInput)


class CartDeliveryInfoFormWithoutDelivery(forms.Form):
    fullname = forms.CharField(required=True, widget=forms.HiddenInput)
    email = forms.EmailField(required=True, widget=forms.HiddenInput)
    phone = forms.CharField(required=True, widget=forms.HiddenInput, initial='')
    billing_address = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    billing_postal_code = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    billing_city = forms.CharField(required=False, widget=forms.HiddenInput, initial='')
    product_note = forms.CharField(required=False, widget=forms.HiddenInput, initial='')


class CartDeliveryInfoFormWithoutDeliveryNotHidden(forms.Form):
    full_name = forms.CharField(required=True, label='Teljes név*',
                                widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'full_name'}))
    phone = forms.CharField(required=True, initial='', label='Telefonszám*',
                            widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'phone_number'}))
    email = forms.EmailField(required=True, label='E-mail cím*',
                             widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'email_address'}))
    billing_address = forms.CharField(required=True, initial='', label='Utca, házszám*',
                                      widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'billing_address'}))
    billing_postal_code = forms.CharField(required=True, initial='', label='Irányítószám*', widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'billing_postal_code'}))
    billing_city = forms.CharField(required=True, initial='', label='Település*',
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'billing_city'}))
    product_note = forms.CharField(required=False, initial='', label='Megjegyzés',
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'product_note'}))
