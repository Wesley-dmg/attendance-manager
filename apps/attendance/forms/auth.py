# forms/auth.py
from django import forms


class RequestOTPForm(forms.Form):
    phone = forms.CharField(
        label="Numéro de téléphone",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ex: +22912345678",
            }
        ),
    )


class VerifyOTPForm(forms.Form):
    phone = forms.CharField(widget=forms.HiddenInput(), required=False)
    code = forms.CharField(
        label="Code OTP",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Entrez le code OTP reçu par WhatsApp",
            }
        ),
    )
