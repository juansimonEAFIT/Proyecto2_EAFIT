from django import forms
from .models import SolicitudTiquete


class FormularioSolicitudTiquete(forms.ModelForm):
    class Meta:
        model = SolicitudTiquete
        fields = ["tipo_tiquete"]
        labels = {
            "tipo_tiquete": "¿Cómo deseas tu tiquete de almuerzo?",
        }
