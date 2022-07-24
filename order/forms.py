from django import forms

from .models import Order


class OrderCreateForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['full_name', 'first_name', 'delivery_type_code', 'last_name', 'email', 'address', 'address_number',
                  'postal_code', 'city', 'note', 'fox_post', 'delivery_name',
                  'phone', 'csomagkuldo', 'billing_address', 'billing_address_number',
                  'billing_postal_code', 'billing_city', 'product_note']
