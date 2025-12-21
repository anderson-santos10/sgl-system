from django import forms
from transport.models import Lecom


class TransporteForm(forms.ModelForm):
    class Meta:
        model = Lecom
        fields = ["data", ...]
