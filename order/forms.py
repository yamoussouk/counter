from django import forms

from .models import Order


class OrderCreateForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['full_name', 'first_name', 'delivery_type', 'last_name', 'email', 'address',
                  'postal_code', 'city', 'note', 'fox_post', 'delivery_name', 'phone', 'csomagkuldo',
                  'billing_address', 'billing_postal_code', 'billing_city']
