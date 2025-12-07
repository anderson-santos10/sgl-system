from django import forms
from .models import Transport

class TransportForm(forms.ModelForm):
    class Meta:
        model = Transport
        fields = [
            "lecom",
            "carga",
            "seq",
            "destino",
            "uf",
            "peso",
            "m3",
            "entregas",
            "mod",
            "observacao",
            "tipo_veiculo",
            "status",
            "data",
        ]
