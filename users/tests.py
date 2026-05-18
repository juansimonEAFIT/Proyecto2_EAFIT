from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from users.models import Empleado, Restaurante

User = get_user_model()

class UserTestBase(TestCase):
    """
    Clase base para pruebas de usuario. 
    Aplica el principio de Responsabilidad Única (SRP) al centralizar la creación de datos.
    """
    def setUp(self):
        self.client = Client()
        self.password = 'testpassword123'
        self.admin_role = 'administrador'
        self.empleado_role = 'empleado'
        self.restaurante_role = 'restaurante'

    def create_test_user(self, username, role='empleado', is_staff=False, is_superuser=False, **kwargs):
        """Helper para crear usuarios de prueba de forma consistente."""
        create_method = User.objects.create_superuser if is_superuser else User.objects.create_user
        user = create_method(
            username=username,
            password=self.password,
            role=role,
            **kwargs
        )
        return user

    def login_as(self, user):
        """Helper para iniciar sesión con un usuario."""
        self.client.force_login(user)

    def assert_message_contains(self, response, expected_text):
        """Helper para verificar mensajes en la respuesta."""
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(expected_text in str(m) for m in messages),
            f"No se encontró '{expected_text}' en los mensajes: {messages}"
        )

class LoginTests(UserTestBase):
    def setUp(self):
        super().setUp()
        self.login_url = reverse('login')
        self.username = 'testuser'
        self.user = self.create_test_user(username=self.username, role=self.empleado_role)

    def test_login_view_get(self):
        """Prueba que la página de login cargue correctamente."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_login_success_empleado(self):
        """Prueba que un empleado pueda iniciar sesión exitosamente y sea redirigido."""
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': self.password
        })
        # Debe redirigir al dashboard del empleado
        self.assertRedirects(response, reverse('dashboard_empleado'))

    def test_login_invalid_credentials(self):
        """
        CP-02: Verificación inicio de sesión no exitoso (por credenciales invalidas).
        """
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        # El sistema debe mostrar un mensaje de error indicando que las credenciales son incorrectas
        self.assert_message_contains(response, "Contraseña incorrecta")
        # Verificar que no se inició sesión (el cliente no tiene el ID del usuario en la sesión)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_nonexistent_user(self):
        """
        CP-02: Verificación inicio de sesión no exitoso (usuario inválido).
        """
        response = self.client.post(self.login_url, {
            'username': 'nonexistent',
            'password': 'somepassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assert_message_contains(response, "El usuario no existe")
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_inactive_user(self):
        """Prueba que un usuario inactivo no pueda iniciar sesión."""
        self.user.is_active = False
        self.user.save()
        
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': self.password
        })
        self.assertEqual(response.status_code, 200)
        self.assert_message_contains(response, "cuenta ha sido desactivada")

    def test_login_redirect_by_role_admin(self):
        """Prueba la redirección correcta para el rol administrador."""
        self.create_test_user(username='adminuser', role=self.admin_role)
        response = self.client.post(self.login_url, {
            'username': 'adminuser',
            'password': self.password
        })
        self.assertRedirects(response, reverse('dashboard_admin'))

    def test_login_redirect_by_role_restaurante(self):
        """Prueba la redirección correcta para el rol restaurante."""
        self.create_test_user(username='restuser', role=self.restaurante_role)
        response = self.client.post(self.login_url, {
            'username': 'restuser',
            'password': self.password
        })
        self.assertRedirects(response, reverse('dashboard_restaurante'))

class RoleManagementTests(UserTestBase):
    def setUp(self):
        super().setUp()
        self.admin_user = self.create_test_user(
            username='admin', 
            email='admin@test.com', 
            role=self.admin_role, 
            is_superuser=True
        )
        self.target_user = self.create_test_user(username='targetuser', role=self.empleado_role)
        self.login_as(self.admin_user)

    def test_admin_can_access_gestion_personal(self):
        """Prueba que el admin puede acceder a la vista de gestión de personal."""
        response = self.client.get(reverse('editar_personal', args=[self.target_user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/gestion_personal.html')

    def test_admin_can_change_user_role_to_restaurante(self):
        """
        CP-03: Verificación de asignación de roles a usuarios por el administrador.
        """
        url = reverse('editar_personal', args=[self.target_user.id])
        data = {
            'username': 'targetuser_updated', # Cambiamos username para forzar que el formulario procese
            'email': 'target@test.com',
            'first_name': 'Target',
            'last_name': 'User',
            'role': self.restaurante_role,
            'password': self.password, # Proporcionamos la contraseña explícitamente
            'nombre_sede': 'Sede Test',
            'telefono': '1234567'
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('dashboard_admin'))
        
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.role, self.restaurante_role)
        self.assertTrue(Restaurante.objects.filter(user=self.target_user).exists())

        # Verificar que el usuario ahora es redirigido correctamente según su nuevo rol
        self.client.logout()
        
        login_response = self.client.post(reverse('login'), {
            'username': 'targetuser_updated',
            'password': self.password
        })
        
        # El código 302 es el redireccionamiento inicial tras el login
        self.assertEqual(login_response.status_code, 302)
        self.assertEqual(login_response.url, reverse('dashboard_restaurante'))

    def test_admin_can_assign_role_at_creation(self):
        """Prueba que el administrador puede asignar un rol al crear un nuevo usuario."""
        url = reverse('crear_personal')
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'first_name': 'New',
            'last_name': 'User',
            'role': self.empleado_role,
            'password': 'newpassword123',
            'numero_documento': '987654321',
            'departamento': 'TI',
            'telefono': '7654321'
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('dashboard_admin'))
        
        new_user = User.objects.get(username='newuser')
        self.assertEqual(new_user.role, self.empleado_role)
        self.assertTrue(Empleado.objects.filter(user=new_user).exists())

    def test_non_admin_cannot_access_role_management(self):
        """Prueba que un usuario no administrador no puede acceder a la gestión de personal."""
        self.client.logout()
        regular_user = self.create_test_user(username='regular', role=self.empleado_role)
        self.login_as(regular_user)
        
        response = self.client.get(reverse('crear_personal'))
        self.assertRedirects(response, reverse('dashboard_empleado'))

    def test_cambio_estado_usuario(self):
        url = reverse("cambiar_estado_usuario", args=[self.target_user.id])

        estado_inicial = self.target_user.is_active

        self.client.get(url)

        self.target_user.refresh_from_db()

        self.assertNotEqual(self.target_user.is_active, estado_inicial)


class UserCreationTests(UserTestBase):
    """
    CP-04 Creacion de Empleados o Restaurantes Exitosa.
    Refactorizado siguiendo SOLID.
    """
    def setUp(self):
        super().setUp()
        self.admin_user = self.create_test_user(
            username='admin_creator',
            email='admin_creator@test.com',
            role=self.admin_role,
            is_superuser=True
        )
        self.login_as(self.admin_user)
        self.url = reverse('crear_personal')

    def test_creacion_exitosa_empleado(self):
        """Verifica la creación exitosa de un empleado con datos válidos."""
        data = {
            'username': 'empleado_nuevo',
            'first_name': 'Juan',
            'last_name': 'Perez',
            'email': 'juan.perez@test.com',
            'password': self.password,
            'role': self.empleado_role,
            'numero_documento': '1000200300',
            'departamento': 'Logística',
            'telefono': '3001234567'
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('dashboard_admin'))
        
        user = User.objects.get(username='empleado_nuevo')
        self.assertEqual(user.role, self.empleado_role)
        
        perfil = Empleado.objects.get(user=user)
        self.assertEqual(perfil.numero_documento, '1000200300')

    def test_creacion_exitosa_restaurante(self):
        """Verifica la creación exitosa de un restaurante con datos válidos."""
        data = {
            'username': 'restaurante_nuevo',
            'first_name': 'Sede',
            'last_name': 'Norte',
            'email': 'norte@restaurante.com',
            'password': self.password,
            'role': self.restaurante_role,
            'nombre_sede': 'Restaurante Sede Norte',
            'telefono': '601234567'
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('dashboard_admin'))
        
        user = User.objects.get(username='restaurante_nuevo')
        self.assertEqual(user.role, self.restaurante_role)
        
        perfil = Restaurante.objects.get(user=user)
        self.assertEqual(perfil.nombre_sede, 'Restaurante Sede Norte')

    def test_error_usuario_duplicado(self):
        """Verifica que no se permita crear un usuario con un username ya existente."""
        self.create_test_user(username='existente', role=self.empleado_role)
        
        data = {
            'username': 'existente',
            'first_name': 'Otro',
            'last_name': 'Usuario',
            'email': 'otro@test.com',
            'password': self.password,
            'role': self.empleado_role,
            'numero_documento': '999888777',
            'departamento': 'Ventas'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        form = response.context['formulario']
        self.assertIn('username', form.errors)
        self.assertEqual(form.errors['username'][0], 'Este nombre de usuario ya está en uso.')

    def test_error_correo_duplicado(self):
        """Verifica que no se permita crear un usuario con un correo ya existente."""
        self.create_test_user(username='u1', email='dup@test.com', role=self.empleado_role)
        
        data = {
            'username': 'u2',
            'first_name': 'Otro',
            'last_name': 'Usuario',
            'email': 'dup@test.com',
            'password': self.password,
            'role': self.empleado_role,
            'numero_documento': '999888776',
            'departamento': 'Ventas'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        form = response.context['formulario']
        self.assertIn('email', form.errors)
        self.assertEqual(form.errors['email'][0], 'Este correo ya está en uso.')

    def test_error_documento_duplicado(self):
        """Verifica que no se permita crear un empleado con un número de documento ya existente."""
        u1 = self.create_test_user(username='u1', role=self.empleado_role)
        Empleado.objects.filter(user=u1).update(numero_documento='12345')
        
        data = {
            'username': 'u2',
            'first_name': 'Otro',
            'last_name': 'Usuario',
            'email': 'u2@test.com',
            'password': self.password,
            'role': self.empleado_role,
            'numero_documento': '12345',
            'departamento': 'Ventas'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        form = response.context['formulario']
        self.assertIn('numero_documento', form.errors)
        self.assertEqual(form.errors['numero_documento'][0], 'Este número de documento ya está registrado.')

class UserCreationFailureTests(UserTestBase):
    """
    CP-05 Creacion de Empleados o Restaurantes Erronea.
    """
    def setUp(self):
        super().setUp()
        self.admin_user = self.create_test_user(
            username='admin_tester',
            role=self.admin_role,
            is_superuser=True
        )
        self.login_as(self.admin_user)
        self.url = reverse('crear_personal')

    def test_creacion_fallida_campos_vacios(self):
        """Verifica que el sistema no permita la creación con campos obligatorios vacíos."""
        data = {
            'username': '',
            'email': '',
            'password': '',
            'role': self.empleado_role
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        # El formulario debe contener errores
        form = response.context['formulario']
        self.assertTrue(form.errors)
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('password', form.errors)

    def test_creacion_fallida_correo_invalido(self):
        """Verifica que el sistema rechace correos electrónicos con formato inválido."""
        data = {
            'username': 'user_bad_email',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'correo-no-valido',
            'password': self.password,
            'role': self.empleado_role,
            'numero_documento': '123456',
            'departamento': 'TI'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        form = response.context['formulario']
        self.assertIn('email', form.errors)
        # Ajustamos al mensaje exacto de Django en español
        self.assertTrue(
            any('dirección de correo electrónico válida' in err for err in form.errors['email'])
        )

    def test_creacion_fallida_documento_obligatorio_empleado(self):
        """Verifica que un empleado requiera obligatoriamente el número de documento."""
        data = {
            'username': 'empleado_sin_doc',
            'first_name': 'Sin',
            'last_name': 'Doc',
            'email': 'sindoc@test.com',
            'password': self.password,
            'role': self.empleado_role,
            'numero_documento': '', # Vacío
            'departamento': 'TI'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        form = response.context['formulario']
        self.assertIn('numero_documento', form.errors)
        self.assertEqual(form.errors['numero_documento'][0], 'El número de documento es obligatorio para empleados.')


class UserActionsTest(UserTestBase):

    def setUp(self):
        super().setUp()
        self.client = Client()
        self.user = User.objects.create_user(
            username="empleado_perfil_acciones",
            password="123",
            role="empleado",
            first_name="Old"
        )

        self.login_as(self.user)

    def test_edicion_usuario_exitosa(self):
        response = self.client.post(reverse("editar_perfil"), {
            "first_name": "NuevoNombre",
            "last_name": self.user.last_name or "Apellido",
            "email": self.user.email or "test@test.com",
            "departamento": "TI",
            "telefono": "123456"
        })

        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()

        self.assertEqual(self.user.first_name, "NuevoNombre")

    def test_edicion_usuario_erronea(self):
        response = self.client.post(reverse("editar_perfil"), {
            "email": "email_invalido"  # formato incorrecto
        })

        self.assertEqual(response.status_code, 200)

        form = response.context["formulario"]

        self.assertTrue(form.errors)
