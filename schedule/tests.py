import csv
from decimal import Decimal
from io import StringIO

from django.test import TestCase
from django.urls import reverse

from schedule.models import Consumo, RegistroPago
from users.models import User


class ExportacionReportesTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin_reportes",
            password="ClaveSegura123",
            role="administrador",
            first_name="Ana",
            last_name="Admin",
        )
        self.empleado_user = User.objects.create_user(
            username="empleado_reportes",
            password="ClaveSegura123",
            role="empleado",
            first_name="Eva",
            last_name="Empleado",
        )
        self.empleado = self.empleado_user.empleado_perfil
        self.empleado.numero_documento = "123456789"
        self.empleado.departamento = "Finanzas"
        self.empleado.save()
        self.otro_empleado_user = User.objects.create_user(
            username="empleado_otro",
            password="ClaveSegura123",
            role="empleado",
            first_name="Luis",
            last_name="Otra",
        )
        self.otro_empleado = self.otro_empleado_user.empleado_perfil
        self.otro_empleado.numero_documento = "987654321"
        self.otro_empleado.departamento = "Compras"
        self.otro_empleado.save()

    def _leer_csv(self, response):
        contenido = response.content.decode("utf-8-sig")
        return list(csv.DictReader(StringIO(contenido)))

    def test_admin_puede_exportar_reporte_de_consumos(self):
        Consumo.objects.create(empleado=self.empleado)
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("exportar_reporte_consumos"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn("reporte_consumos_", response["Content-Disposition"])
        filas = self._leer_csv(response)
        self.assertEqual(len(filas), 1)
        self.assertEqual(filas[0]["Empleado"], "Eva Empleado")
        self.assertEqual(filas[0]["Usuario"], "empleado_reportes")
        self.assertEqual(filas[0]["Documento"], "123456789")
        self.assertEqual(filas[0]["Departamento"], "Finanzas")
        self.assertTrue(filas[0]["Fecha consumo"])

    def test_admin_puede_exportar_reporte_de_consumos_en_excel(self):
        Consumo.objects.create(empleado=self.empleado)
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("exportar_reporte_consumos"), {"formato": "excel"})

        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment; filename=", response["Content-Disposition"])
        self.assertTrue(
            "spreadsheetml" in response["Content-Type"] or "excel" in response["Content-Type"]
        )
        self.assertTrue(response.content.startswith(b"PK") or response.content.startswith(b"\xef\xbb\xbf"))

    def test_admin_puede_exportar_reporte_de_consumos_en_pdf(self):
        Consumo.objects.create(empleado=self.empleado)
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("exportar_reporte_consumos"), {"formato": "pdf"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn(".pdf", response["Content-Disposition"])
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_reporte_de_consumos_respeta_filtro_por_empleado(self):
        Consumo.objects.create(empleado=self.empleado)
        Consumo.objects.create(empleado=self.otro_empleado)
        self.client.force_login(self.admin_user)

        response = self.client.get(
            reverse("exportar_reporte_consumos"),
            {"empleado": str(self.empleado.id)},
        )

        filas = self._leer_csv(response)
        self.assertEqual(len(filas), 1)
        self.assertEqual(filas[0]["Usuario"], "empleado_reportes")

    def test_admin_puede_exportar_reporte_de_pagos(self):
        RegistroPago.objects.create(
            empleado=self.empleado,
            valor_pagado=Decimal("25000.00"),
            comprobante="TRX-001",
            validado_por_gh=True,
            confirmado_por_empleado=True,
        )
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("exportar_reporte_pagos"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn("reporte_pagos_", response["Content-Disposition"])
        filas = self._leer_csv(response)
        self.assertEqual(len(filas), 1)
        self.assertEqual(filas[0]["Empleado"], "Eva Empleado")
        self.assertEqual(filas[0]["Usuario"], "empleado_reportes")
        self.assertEqual(filas[0]["Documento"], "123456789")
        self.assertEqual(filas[0]["Valor pagado"], "25000.00")
        self.assertEqual(filas[0]["Comprobante"], "TRX-001")
        self.assertEqual(filas[0]["Validado por GH"], "Si")
        self.assertEqual(filas[0]["Confirmado por empleado"], "Si")
        self.assertTrue(filas[0]["Fecha pago"])

    def test_admin_puede_exportar_reporte_de_pagos_en_excel(self):
        RegistroPago.objects.create(
            empleado=self.empleado,
            valor_pagado=Decimal("25000.00"),
            comprobante="TRX-001",
        )
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("exportar_reporte_pagos"), {"formato": "excel"})

        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment; filename=", response["Content-Disposition"])
        self.assertTrue(
            "spreadsheetml" in response["Content-Type"] or "excel" in response["Content-Type"]
        )
        self.assertTrue(response.content.startswith(b"PK") or response.content.startswith(b"\xef\xbb\xbf"))

    def test_admin_puede_exportar_reporte_de_pagos_en_pdf(self):
        RegistroPago.objects.create(
            empleado=self.empleado,
            valor_pagado=Decimal("25000.00"),
            comprobante="TRX-001",
        )
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("exportar_reporte_pagos"), {"formato": "pdf"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn(".pdf", response["Content-Disposition"])
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_reporte_de_pagos_respeta_filtro_por_validacion(self):
        RegistroPago.objects.create(
            empleado=self.empleado,
            valor_pagado=Decimal("25000.00"),
            comprobante="TRX-001",
            validado_por_gh=True,
        )
        RegistroPago.objects.create(
            empleado=self.otro_empleado,
            valor_pagado=Decimal("10000.00"),
            comprobante="TRX-002",
            validado_por_gh=False,
        )
        self.client.force_login(self.admin_user)

        response = self.client.get(
            reverse("exportar_reporte_pagos"),
            {"validado": "si"},
        )

        filas = self._leer_csv(response)
        self.assertEqual(len(filas), 1)
        self.assertEqual(filas[0]["Usuario"], "empleado_reportes")
        self.assertEqual(filas[0]["Validado por GH"], "Si")

    def test_empleado_no_puede_exportar_reportes_administrativos(self):
        self.client.force_login(self.empleado_user)

        response = self.client.get(reverse("exportar_reporte_consumos"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard_empleado"))
