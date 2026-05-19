from django.test import TestCase, Client
from django.urls import reverse
import json

from users.models import User, Empleado
from schedule.models import Consumo


class TestAnalyticsDashboard(TestCase):

    def setUp(self):
        self.client = Client()

        self.admin = User.objects.create_user(
            username="admin_analytics",
            password="123",
            role="administrador"
        )

        user = User.objects.create_user(
            username="empleado_analytics",
            password="123",
            role="empleado"
        )

        self.empleado = user.empleado_perfil

        # Crear consumos
        Consumo.objects.create(empleado=self.empleado)
        Consumo.objects.create(empleado=self.empleado)

    def test_dashboard_muestra_datos_correctos(self):
        self.client.login(username="admin_analytics", password="123")

        response = self.client.get(reverse("analytics_overview"), {
            "show_used": "on"
        })

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.context["chart_data_json"])

        self.assertTrue(len(data["labels"]) > 0)
        self.assertEqual(sum(data["used"]), 2)