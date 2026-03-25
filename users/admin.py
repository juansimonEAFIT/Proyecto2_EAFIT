from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Rol', {'fields': ('role', 'qr_token')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información de Rol', {'fields': ('role', 'qr_token')}),
    )
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
