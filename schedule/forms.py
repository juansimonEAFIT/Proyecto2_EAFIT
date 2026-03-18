from django import forms
from .models import SolicitudTiquete, RegistroPago, InventarioTiquetes


class FormularioSolicitudTiquete(forms.ModelForm):
    class Meta:
        model = SolicitudTiquete
        fields = ["cantidad", "fecha_reclamo"]
        widgets = {
            "fecha_reclamo": forms.DateInput(attrs={"type": "date"}),
        }
        labels = {
            "cantidad": "Cantidad requerida",
            "fecha_reclamo": "Fecha en la que realizarás el reclamo",
        }


class FormularioRegistroPago(forms.ModelForm):
    class Meta:
        model = RegistroPago
        fields = ["valor_pagado", "comprobante"]
        labels = {
            "valor_pagado": "Valor pagado",
            "comprobante": "Referencia del comprobante",
        }


class FormularioInventario(forms.ModelForm):
    class Meta:
        model = InventarioTiquetes
        fields = ["mes", "cantidad_inicial", "max_tiquetes_por_empleado"]
        widgets = {
            "mes": forms.DateInput(attrs={"type": "date"}),
        }
