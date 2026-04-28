from django import forms
from django.utils import timezone
from django.db.models import Sum, F
from decimal import Decimal
from users.models import Empleado
from .models import SolicitudTiquete, RegistroPago, InventarioTiquetes, Consumo


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


class EmpleadoConDeudaChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        tiquetes_aprobados = SolicitudTiquete.objects.filter(empleado=obj, estado="aprobado").annotate(
            costo_total=F('cantidad') * F('precio_unitario')
        ).aggregate(total=Sum('costo_total'))["total"] or Decimal("0.00")
        
        total_pagos_validados = RegistroPago.objects.filter(empleado=obj, validado_por_gh=True).aggregate(total=Sum("valor_pagado"))["total"] or Decimal("0.00")
        
        saldo_pendiente = tiquetes_aprobados - total_pagos_validados
        
        nombre = obj.user.get_full_name() or obj.user.username
        if saldo_pendiente > 0:
            return f"{nombre} - ${saldo_pendiente:,.0f}".replace(",", ".")
        else:
            return f"{nombre} - Paz y salvo"


class EmpleadoSelectWidget(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        # Extract the debt from the label returned by label_from_instance
        label_str = str(label)
        if ' - ' in label_str:
            parts = label_str.split(' - ')
            option['attrs']['data-deuda'] = parts[1]
            option['label'] = parts[0]
        return option


class FormularioRegistroPagoAdmin(forms.ModelForm):
    empleado = EmpleadoConDeudaChoiceField(
        queryset=Empleado.objects.none(),
        label="Empleado",
        empty_label="Seleccione un empleado...",
        widget=EmpleadoSelectWidget(attrs={"class": "form-control"})
    )

    class Meta:
        model = RegistroPago
        fields = ["empleado", "valor_pagado"]
        labels = {
            "empleado": "Empleado",
            "valor_pagado": "Valor a pagar ($)",
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar empleados activos
        qs = Empleado.objects.filter(esta_activo=True).select_related("user").order_by("user__first_name")
        self.fields["empleado"].queryset = qs

    def clean_valor_pagado(self):
        valor = self.cleaned_data.get("valor_pagado")
        if valor is None or valor <= 0:
            raise forms.ValidationError("El valor pagado debe ser mayor a 0.")
        return valor

    def clean(self):
        cleaned_data = super().clean()
        empleado = cleaned_data.get("empleado")
        valor_pagado = cleaned_data.get("valor_pagado")

        if empleado and valor_pagado:
            # Calcular la deuda actual del empleado
            tiquetes_aprobados = SolicitudTiquete.objects.filter(empleado=empleado, estado="aprobado").annotate(
                costo_total=F('cantidad') * F('precio_unitario')
            ).aggregate(total=Sum('costo_total'))["total"] or Decimal("0.00")
            
            total_pagos_validados = RegistroPago.objects.filter(empleado=empleado, validado_por_gh=True).aggregate(total=Sum("valor_pagado"))["total"] or Decimal("0.00")
            
            saldo_pendiente = tiquetes_aprobados - total_pagos_validados
            
            if valor_pagado > saldo_pendiente:
                raise forms.ValidationError(
                    f"El pago (${valor_pagado}) excede la deuda actual del empleado (${saldo_pendiente}). No se permite saldo a favor."
                )
        return cleaned_data



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

    def __init__(self, *args, **kwargs):
        ya_existe = kwargs.pop("ya_existe", False)
        super().__init__(*args, **kwargs)
        if ya_existe:
            self.fields["mes"].widget.attrs["readonly"] = True
            self.fields["cantidad_inicial"].widget.attrs["readonly"] = True
            self.fields["mes"].required = False
            self.fields["cantidad_inicial"].required = False

    def clean_mes(self):
        mes = self.cleaned_data.get("mes")
        if self.instance.pk and mes != self.instance.mes:
            return self.instance.mes
        return mes

    def clean_cantidad_inicial(self):
        cantidad = self.cleaned_data.get("cantidad_inicial")
        if self.instance.pk and 'cantidad_inicial' in self.changed_data:
            # Si ya existe, no permitimos cambiar el inicial desde este form para evitar reseteos
            return self.instance.cantidad_inicial
        return cantidad


class FormularioAumentarInventario(forms.Form):
    cantidad_a_adicionar = forms.IntegerField(
        min_value=1, 
        label="Cantidad a adicionar",
        help_text="Sumará esta cantidad al stock disponible actual."
    )


class FormularioEditarConsumo(forms.ModelForm):
    motivo = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Explica brevemente el motivo de la corrección..."}),
        label="Motivo de la corrección",
        required=True,
        help_text="Este motivo quedará registrado en el historial de auditoría."
    )

    class Meta:
        model = Consumo
        fields = ["empleado", "fecha_consumo"]
        widgets = {
            "fecha_consumo": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M"
            ),
        }
        labels = {
            "empleado": "Empleado",
            "fecha_consumo": "Fecha y hora del consumo",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Precargar el datetime en formato compatible con datetime-local input
        if self.instance and self.instance.fecha_consumo:
            from django.utils import timezone as tz
            local_dt = tz.localtime(self.instance.fecha_consumo)
            self.initial["fecha_consumo"] = local_dt.strftime("%Y-%m-%dT%H:%M")
        # Mostrar solo empleados activos
        from users.models import Empleado as EmpleadoModel
        self.fields["empleado"].queryset = EmpleadoModel.objects.filter(
            esta_activo=True
        ).select_related("user").order_by("user__first_name")
