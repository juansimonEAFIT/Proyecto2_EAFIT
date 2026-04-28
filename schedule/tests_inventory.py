from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from schedule.models import InventarioTiquetes
from users.models import User
from decimal import Decimal

class InventarioTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin",
            password="adminpassword",
            email="admin@test.com"
        )
        self.admin.role = "administrador"
        self.admin.save()
        self.client.force_login(self.admin)

    def test_crear_inventario_mensual(self):
        """Verifica que se puede crear un inventario si no existe para el mes."""
        url = reverse("gestionar_inventario")
        hoy = timezone.now().date()
        
        response = self.client.post(url, {
            "mes": hoy.isoformat(),
            "cantidad_inicial": 100,
            "max_tiquetes_por_empleado": 20,
            "precio_tiquete": "10000.00"
        })
        
        self.assertEqual(response.status_code, 302)
        inv = InventarioTiquetes.objects.get(mes__month=hoy.month, mes__year=hoy.year)
        self.assertEqual(inv.cantidad_inicial, 100)
        self.assertEqual(inv.cantidad_disponible, 100)

    def test_bloqueo_campos_si_ya_existe(self):
        """Verifica que si ya existe el inventario, no se puede cambiar cantidad_inicial desde el form principal."""
        hoy = timezone.now().date()
        inv_existente = InventarioTiquetes.objects.create(
            mes=hoy,
            cantidad_inicial=100,
            cantidad_disponible=100,
            max_tiquetes_por_empleado=20,
            precio_tiquete=Decimal("10000.00")
        )
        
        url = reverse("gestionar_inventario")
        # Intentamos cambiar cantidad_inicial a 500
        response = self.client.post(url, {
            "mes": hoy.isoformat(),
            "cantidad_inicial": 500,
            "max_tiquetes_por_empleado": 25,
            "precio_tiquete": "12000.00"
        })
        
        inv_existente.refresh_from_db()
        # cantidad_inicial no debe haber cambiado
        self.assertEqual(inv_existente.cantidad_inicial, 100)
        # Otros campos sí pueden cambiar
        self.assertEqual(inv_existente.max_tiquetes_por_empleado, 25)
        self.assertEqual(inv_existente.precio_tiquete, Decimal("12000.00"))

    def test_aumentar_inventario(self):
        """Verifica que la vista de aumento funciona correctamente."""
        hoy = timezone.now().date()
        inv = InventarioTiquetes.objects.create(
            mes=hoy,
            cantidad_inicial=100,
            cantidad_disponible=80,
            max_tiquetes_por_empleado=20,
            precio_tiquete=Decimal("10000.00")
        )
        
        url = reverse("aumentar_inventario")
        response = self.client.post(url, {
            "cantidad_a_adicionar": 50
        })
        
        self.assertEqual(response.status_code, 302)
        inv.refresh_from_db()
        self.assertEqual(inv.cantidad_disponible, 130) # 80 + 50
        self.assertEqual(inv.cantidad_inicial, 150)    # 100 + 50
