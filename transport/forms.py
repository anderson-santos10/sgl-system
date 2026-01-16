from django import forms
from transport.models import Lecom


class TransporteForm(forms.ModelForm):
    class Meta:
        model = Lecom
        fields = '__all__'

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            self.fields['status'].initial = 'BLOQUEADO'