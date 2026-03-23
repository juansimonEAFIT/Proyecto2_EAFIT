from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Empleado, Restaurante, Administrador


@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.role == "empleado":
        Empleado.objects.create(user=instance)
    elif instance.role == "restaurante":
        Restaurante.objects.create(user=instance)
    elif instance.role == "administrador":
        Administrador.objects.create(user=instance)