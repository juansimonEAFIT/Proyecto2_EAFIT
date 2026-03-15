from django import forms
from django.contrib.auth.models import User
from .models import Empleado


class FormularioCreacionEmpleado(forms.Form):
    nombre = forms.CharField(max_length=100)
    apellido = forms.CharField(max_length=100)
    nombre_usuario = forms.CharField(max_length=150)
    correo = forms.EmailField()
    numero_documento = forms.CharField(max_length=50)
    departamento = forms.CharField(max_length=100, required=False)
    telefono = forms.CharField(max_length=20, required=False)
    contrasena = forms.CharField(widget=forms.PasswordInput)

    def clean_nombre_usuario(self):
        nombre_usuario = self.cleaned_data["nombre_usuario"]
        if User.objects.filter(username=nombre_usuario).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso.")
        return nombre_usuario

    def clean_correo(self):
        correo = self.cleaned_data["correo"]
        if User.objects.filter(email=correo).exists():
            raise forms.ValidationError("Este correo ya está en uso.")
        return correo

    def clean_numero_documento(self):
        numero_documento = self.cleaned_data["numero_documento"]
        if Empleado.objects.filter(numero_documento=numero_documento).exists():
            raise forms.ValidationError("Este número de documento ya está registrado.")
        return numero_documento


class FormularioAsignacionRol(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ["rol", "esta_activo"]
