from django import forms
from django.utils import timezone
from .models import SolicitudTiquete, RegistroPago, InventarioTiquetes


class FormularioSolicitudTiquete(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.empleado = kwargs.pop("empleado", None)
        super().__init__(*args, **kwargs)
        # Forzar cantidad a 1 y ocultarla si se prefiere, o simplemente no incluirla en el form
        # Si el usuario quiere verla, la dejamos como 1 y deshabilitada/readonly
        self.fields["cantidad"].initial = 1
        self.fields["cantidad"].widget.attrs["readonly"] = True

    class Meta:
        model = SolicitudTiquete
        fields = ["fecha_reclamo", "cantidad"]
        widgets = {
            "fecha_reclamo": forms.DateInput(attrs={"type": "date", "min": timezone.localdate().isoformat()}),
        }
        labels = {
            "cantidad": "Cantidad (máximo 1)",
            "fecha_reclamo": "Fecha en la que realizarás el reclamo",
        }

    def clean_fecha_reclamo(self):
        fecha = self.cleaned_data.get("fecha_reclamo")
        if not fecha:
            return fecha

        # 1. No permitir fechas pasadas
        hoy = timezone.localdate()
        if fecha < hoy:
            raise forms.ValidationError("No puedes solicitar tiquetes para fechas pasadas.")

        # 2. Un solo tiquete por día
        if self.empleado:
            # Buscar si ya existe una solicitud para esa fecha (pendiente o aprobada)
            existe = SolicitudTiquete.objects.filter(
                empleado=self.empleado,
                fecha_reclamo=fecha,
                estado__in=["pendiente", "aprobado"]
            ).exists()
            if existe:
                raise forms.ValidationError(f"Ya tienes una solicitud de tiquete para el día {fecha}.")

        return fecha

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get("cantidad")
        if cantidad != 1:
            raise forms.ValidationError("Solo puedes pedir un tiquete por día.")
        return cantidad


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
        fields = ["mes", "cantidad_inicial", "max_tiquetes_por_empleado", "precio_tiquete"]
        widgets = {
            "mes": forms.DateInput(attrs={"type": "date"}),
        }
        labels = {
            "precio_tiquete": "Precio por tiquete ($)",
        }
