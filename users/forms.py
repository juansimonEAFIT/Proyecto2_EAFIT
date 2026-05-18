from django import forms
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import Empleado, Restaurante

User = get_user_model()


class FormularioPersonal(forms.ModelForm):
    # Campos de User
    first_name = forms.CharField(label="Nombre", max_length=100)
    last_name = forms.CharField(label="Apellido", max_length=100)
    email = forms.EmailField(label="Correo electrónico")
    username = forms.CharField(label="Nombre de usuario", max_length=150)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput, required=False)
    role = forms.ChoiceField(label="Rol en el sistema", choices=User.ROLES)
    
    # Campos comunes/especificos de perfil (los manejaremos en la vista)
    numero_documento = forms.CharField(
        label="Número de Documento", 
        required=False,
        widget=forms.TextInput(attrs={'type': 'text', 'inputmode': 'numeric', 'pattern': '[0-9]*', 'class': 'solo-numeros'})
    )
    departamento = forms.CharField(label="Departamento/Área", required=False)
    telefono = forms.CharField(
        label="Teléfono", 
        required=False,
        widget=forms.TextInput(attrs={'type': 'text', 'inputmode': 'numeric', 'pattern': '[0-9]*', 'class': 'solo-numeros'})
    )
    nombre_sede = forms.CharField(label="Nombre de la Sede (Solo Restaurante)", required=False, initial="Sede Principal")

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "role", "password"]

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            initial = kwargs.get('initial', {})
            # Cargar datos del perfil según el rol
            if instance.role == 'empleado' and hasattr(instance, 'empleado_perfil'):
                initial['numero_documento'] = instance.empleado_perfil.numero_documento
                initial['departamento'] = instance.empleado_perfil.departamento
                initial['telefono'] = instance.empleado_perfil.telefono
                initial['esta_activo'] = instance.empleado_perfil.esta_activo
            elif instance.role == 'restaurante' and hasattr(instance, 'restaurante_perfil'):
                initial['nombre_sede'] = instance.restaurante_perfil.nombre_sede
                initial['telefono'] = instance.restaurante_perfil.telefono
            kwargs['initial'] = initial
        
        super().__init__(*args, **kwargs)
        
        if not instance:
            self.fields['password'].required = True

    def clean_username(self):
        username = self.cleaned_data.get("username")
        qs = User.objects.filter(username=username)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            return email
        qs = User.objects.filter(email=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Este correo ya está en uso.")
        return email

    def clean_numero_documento(self):
        num_doc = self.cleaned_data.get("numero_documento")
        role = self.cleaned_data.get("role")
        
        if role == 'empleado':
            if not num_doc:
                raise forms.ValidationError("El número de documento es obligatorio para empleados.")
            
            # Solo permitir números
            if not num_doc.isdigit():
                raise forms.ValidationError("El número de documento solo debe contener números.")

            # Verificar unicidad
            qs = Empleado.objects.filter(numero_documento=num_doc)
            if self.instance and self.instance.pk:
                # Si estamos editando un usuario, necesitamos excluir su propio perfil de empleado actual
                qs = qs.exclude(user=self.instance)
            
            if qs.exists():
                raise forms.ValidationError("Este número de documento ya está registrado.")
        
        return num_doc

    def clean_telefono(self):
        tel = self.cleaned_data.get("telefono")
        if tel and not tel.isdigit():
            raise forms.ValidationError("El teléfono solo debe contener números.")
        return tel

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        numero_documento = cleaned_data.get("numero_documento")

        if role == 'empleado' and not numero_documento:
            self.add_error('numero_documento', "El número de documento es obligatorio para empleados.")
        
        return cleaned_data

    def save(self, commit=True):
        # Usamos una transacción para asegurar que usuario y perfil se guarden (o no) juntos
        with transaction.atomic():
            user = super().save(commit=False)
            
            # Si hay una contraseña (no vacía), la ciframos
            password = self.cleaned_data.get("password")
            if password and password.strip():
                user.set_password(password)
            
            if commit:
                user.save()
            
            # Lógica de perfiles
            role = self.cleaned_data.get("role")
            
            if role == 'empleado':
                # Crear o actualizar perfil de empleado
                Empleado.objects.update_or_create(
                    user=user,
                    defaults={
                        'numero_documento': self.cleaned_data.get('numero_documento'),
                        'departamento': self.cleaned_data.get('departamento'),
                        'telefono': self.cleaned_data.get('telefono'),
                    }
                )
                # Opcional: Eliminar otros perfiles si existen
                Restaurante.objects.filter(user=user).delete()
                
            elif role == 'restaurante':
                # Crear o actualizar perfil de restaurante
                Restaurante.objects.update_or_create(
                    user=user,
                    defaults={
                        'nombre_sede': self.cleaned_data.get('nombre_sede'),
                        'telefono': self.cleaned_data.get('telefono'),
                    }
                )
                # Opcional: Eliminar otros perfiles si existen
                Empleado.objects.filter(user=user).delete()
            
            return user


class FormularioPerfilEmpleado(forms.ModelForm):
    first_name = forms.CharField(label="Nombre", max_length=100)
    last_name = forms.CharField(label="Apellido", max_length=100)
    email = forms.EmailField(label="Correo electrónico", required=False)
    
    departamento = forms.CharField(label="Departamento/Área", required=False)
    telefono = forms.CharField(
        label="Teléfono", 
        required=False,
        widget=forms.TextInput(attrs={'type': 'text', 'inputmode': 'numeric', 'pattern': '[0-9]*', 'class': 'solo-numeros'})
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance and hasattr(instance, 'empleado_perfil'):
            initial = kwargs.get('initial', {})
            initial['departamento'] = instance.empleado_perfil.departamento
            initial['telefono'] = instance.empleado_perfil.telefono
            kwargs['initial'] = initial
        
        super().__init__(*args, **kwargs)

    def clean_telefono(self):
        tel = self.cleaned_data.get("telefono")
        if tel and not tel.isdigit():
            raise forms.ValidationError("El teléfono solo debe contener números.")
        return tel

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            return email
        qs = User.objects.filter(email=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Este correo ya está en uso.")
        return email

    def save(self, commit=True):
        with transaction.atomic():
            user = super().save(commit=False)
            if commit:
                user.save()
                
                # Actualizar perfil
                if hasattr(user, 'empleado_perfil'):
                    empleado_perfil = user.empleado_perfil
                    empleado_perfil.departamento = self.cleaned_data.get("departamento")
                    empleado_perfil.telefono = self.cleaned_data.get("telefono")
                    empleado_perfil.save()
            
            return user
