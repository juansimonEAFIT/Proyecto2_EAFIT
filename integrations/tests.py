from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch
from schedule.models import Consumo, SolicitudTiquete, InventarioTiquetes
from users.models import User, Empleado
from integrations.views import generar_token_mensual
import uuid


class QRSecurityTests(TestCase):
    def setUp(self):
        # Crear Admin
        self.admin = User.objects.create_superuser(username="admin", password="password", role="administrador")

        # Crear Restaurante
        self.restaurante_user = User.objects.create_user(username="rest_user", password="password", role="restaurante")

        # Crear Empleado
        self.user = User.objects.create_user(username="test_emp", password="password", role="empleado")
        self.empleado = self.user.empleado_perfil
        self.empleado.esta_activo = True
        self.empleado.save()

        # Crear Inventario
        self.hoy = timezone.now()
        self.inv = InventarioTiquetes.objects.create(
            mes=self.hoy.date(),
            cantidad_inicial=100,
            cantidad_disponible=100,
            max_tiquetes_por_empleado=5,
            precio_tiquete=10000
        )

        # Darle tiquetes
        SolicitudTiquete.objects.create(empleado=self.empleado, cantidad=10, estado="aprobado")

    def test_qr_token_generates_differently_per_month(self):
        token_marzo = generar_token_mensual(self.empleado.codigo_qr)

        with patch('django.utils.timezone.now') as mock_now:
            # Simular siguiente mes
            mock_now.return_value = self.hoy + timezone.timedelta(days=32)
            token_abril = generar_token_mensual(self.empleado.codigo_qr)

        self.assertNotEqual(token_marzo, token_abril)

    def test_consumir_qr_rechaza_token_invalido(self):
        self.client.force_login(self.restaurante_user)
        url = reverse("consumir_almuerzo_qr", kwargs={
            "codigo_qr": self.empleado.codigo_qr,
            "token": "token_falso"
        })

        response = self.client.get(url)
        self.assertContains(response, "Código QR expirado o no válido")
        self.assertEqual(Consumo.objects.count(), 0)

    def test_ver_qr_oculta_si_limite_alcanzado(self):
        self.client.force_login(self.user)

        # Consumir hasta el límite (5)
        for _ in range(5):
            Consumo.objects.create(empleado=self.empleado)

        response = self.client.get(reverse("ver_qr_empleado"))
        self.assertContains(response, "Límite Mensual Alcanzado")
        self.assertNotContains(response, "api.qrserver.com")

    def test_consumir_qr_bloquea_si_limite_alcanzado(self):
        self.client.force_login(self.restaurante_user)

        # Consumir hasta el límite
        for _ in range(5):
            Consumo.objects.create(empleado=self.empleado)

        token = generar_token_mensual(self.empleado.codigo_qr)
        url = reverse("consumir_almuerzo_qr", kwargs={
            "codigo_qr": self.empleado.codigo_qr,
            "token": token
        })

        response = self.client.get(url)
        self.assertContains(response, "ya alcanzó su límite")
        self.assertEqual(Consumo.objects.count(), 5)  # Sigue en 5
