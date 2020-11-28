from django import forms


class GiftCardApplyForm(forms.Form):
    unique_uuid = forms.CharField()
