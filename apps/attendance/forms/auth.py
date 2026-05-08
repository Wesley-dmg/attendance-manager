# forms/auth.py
from django import forms


class RequestOTPForm(forms.Form):
    phone = forms.CharField(
        initial="+14193527779",
        label="Numéro de téléphone",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "inputmode": "numeric",  # clavier numérique
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
                "inputmode": "numeric",  # clavier numérique
                "pattern": "[0-9]*",
                "maxlength": "6",  # nombre de chiffres de ton OTP
            }
        ),
    )
