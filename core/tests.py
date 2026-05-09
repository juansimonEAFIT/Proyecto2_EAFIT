from django.test import TestCase
from django.urls import reverse

from users.models import User


class AdminReportesViewTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin_reportes_view",
            password="ClaveSegura123",
            role="administrador",
        )
        self.empleado_user = User.objects.create_user(
            username="empleado_reportes_view",
            password="ClaveSegura123",
            role="empleado",
        )

    def test_admin_puede_ver_pagina_de_reportes(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("dashboard_reportes"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Centro administrativo")
        self.assertContains(response, "Busqueda general")
        self.assertContains(response, "Reporte de consumos")
        self.assertContains(response, "Reporte de pagos")
        self.assertContains(response, reverse("exportar_reporte_consumos"))
        self.assertContains(response, reverse("exportar_reporte_pagos"))

    def test_pagina_de_reportes_conserva_filtros_en_formulario(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(
            reverse("dashboard_reportes"),
            {"buscar": "Eva", "validado": "si"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="Eva"', html=False)
        self.assertContains(response, 'option value="si" selected', html=False)

    def test_empleado_no_puede_ver_pagina_de_reportes(self):
        self.client.force_login(self.empleado_user)

        response = self.client.get(reverse("dashboard_reportes"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard_empleado"))
