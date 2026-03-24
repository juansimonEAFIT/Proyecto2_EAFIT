import uuid

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from schedule.models import Comida, ComidaReservada, Consumo, SolicitudTiquete
from users.models import User


class FlujoQrTests(TestCase):
    def crear_empleado(self, username, numero_documento, esta_activo=True):
        user = User.objects.create_user(
            username=username,
            password="ClaveSegura123",
            role="empleado",
            first_name="Sebastian",
            last_name="Duran",
        )
        empleado = user.empleado_perfil
        empleado.numero_documento = numero_documento
        empleado.esta_activo = esta_activo
        empleado.save()
        return user, empleado

    def crear_restaurante(self, username="restaurante"):
        return User.objects.create_user(
            username=username,
            password="ClaveSegura123",
            role="restaurante",
            first_name="Caja",
            last_name="Principal",
        )

    def test_ver_qr_empleado_expone_url_de_consumo_con_codigo_unico(self):
        user, empleado = self.crear_empleado("empleado_qr", "1001")
        self.client.force_login(user)

        response = self.client.get(reverse("ver_qr_empleado"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(empleado.codigo_qr))
        self.assertContains(response, reverse("consumir_almuerzo_qr", kwargs={"codigo_qr": empleado.codigo_qr}))

    def test_consumir_qr_redirige_a_login_si_no_hay_sesion(self):
        _, empleado = self.crear_empleado("empleado_publico", "1002")

        response = self.client.get(reverse("consumir_almuerzo_qr", kwargs={"codigo_qr": empleado.codigo_qr}))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_consumir_qr_requiere_rol_autorizado(self):
        user, empleado = self.crear_empleado("empleado_intento", "1003")
        self.client.force_login(user)

        response = self.client.get(reverse("consumir_almuerzo_qr", kwargs={"codigo_qr": empleado.codigo_qr}), follow=True)

        self.assertEqual(response.status_code, 200)
        mensajes = [mensaje.message for mensaje in get_messages(response.wsgi_request)]
        self.assertIn("Solo el personal autorizado puede registrar consumos por QR.", mensajes)
        self.assertEqual(Consumo.objects.count(), 0)

    def test_restaurante_puede_registrar_consumo_con_qr_valido(self):
        restaurante = self.crear_restaurante()
        _, empleado = self.crear_empleado("empleado_ok", "1004")
        SolicitudTiquete.objects.create(empleado=empleado, cantidad=1, estado="aprobado")
        Comida.objects.create(nombre="Almuerzo del dia", descripcion="Menu base")
        self.client.force_login(restaurante)

        response = self.client.get(reverse("consumir_almuerzo_qr", kwargs={"codigo_qr": empleado.codigo_qr}), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Consumo.objects.count(), 1)
        consumo = Consumo.objects.get()
        self.assertEqual(consumo.comida.empleado, empleado)
        self.assertTrue(ComidaReservada.objects.filter(empleado=empleado).exists())
        mensajes = [mensaje.message for mensaje in get_messages(response.wsgi_request)]
        self.assertIn(f"Consumo registrado con éxito para {empleado.user.get_full_name()}.", mensajes)

    def test_qr_invalido_muestra_denegado_sin_romper_template(self):
        restaurante = self.crear_restaurante("restaurante_invalido")
        self.client.force_login(restaurante)

        response = self.client.get(
            reverse("consumir_almuerzo_qr", kwargs={"codigo_qr": uuid.uuid4()}),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "DENEGADO")
        self.assertContains(response, "Empleado no encontrado")

    def test_empleado_inactivo_no_puede_consumir_con_qr(self):
        restaurante = self.crear_restaurante("restaurante_inactivo")
        _, empleado = self.crear_empleado("empleado_inactivo", "1005", esta_activo=False)
        SolicitudTiquete.objects.create(empleado=empleado, cantidad=1, estado="aprobado")
        Comida.objects.create(nombre="Almuerzo del dia", descripcion="Menu base")
        self.client.force_login(restaurante)

        response = self.client.get(reverse("consumir_almuerzo_qr", kwargs={"codigo_qr": empleado.codigo_qr}), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Consumo.objects.count(), 0)
        self.assertContains(response, "DENEGADO")
        self.assertContains(response, "inactivo")
