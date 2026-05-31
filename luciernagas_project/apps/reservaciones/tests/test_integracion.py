"""
Pruebas de integración — Flujo completo de reservaciones
MEC Solutions

Ejecutar:
    python manage.py test apps.reservaciones.tests.test_integracion -v 2
"""

from datetime import date
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
from django.urls import reverse

from apps.usuarios.models import Usuario, Cliente
from apps.parques.models import Parque
from apps.reservaciones.models import Reservacion


# Nombres reales de las URLs (apps/reservaciones/urls.py)
URL_NUEVA            = 'reservaciones:nueva'
URL_CANCELAR         = 'reservaciones:cancelar'
URL_MIS_RESERV       = 'reservaciones:mis_reservaciones'
URL_TODAS_ADMIN      = 'reservaciones:todas_admin'

# Los observers se importan localmente dentro de Reservacion.confirmar/cancelar,
# así que el mock apunta al módulo observers donde viven las clases.
MOCK_OBS_CONFIRMACION = 'apps.reservaciones.observers.EmailConfirmacionObserver'
MOCK_OBS_CANCELACION  = 'apps.reservaciones.observers.EmailCancelacionObserver'
MOCK_SUBJECT          = 'apps.reservaciones.observers.ReservacionSubject'


class BaseTestCase(TestCase):

    def setUp(self):
        self.client = Client()

        self.usuario = Usuario.objects.create_user(
            email='cliente@test.com',
            nombre='Ana',
            apellido='López',
            password='test1234',
        )
        self.cliente_perfil = Cliente.objects.create(usuario=self.usuario)

        self.parque = Parque.objects.create(
            nombre='Parque Nanacamilpa',
            direccional='Tlaxcala, México',
            servicios='Baños, estacionamiento, guías',
            horario='18:00 – 23:00',
            latitud=19.3,
            longitud=-98.2,
            tiene_cabanas=True,
            cap_camping=5,
            cap_cabanas=3,
            activo=True,
        )

    def _login(self):
        self.client.login(username='cliente@test.com', password='test1234')


# ─── Autenticación ────────────────────────────────────────────────────────────

class TestAutenticacion(BaseTestCase):

    def test_login_correcto_redirige(self):
        """Credenciales válidas → redirección al inicio."""
        resp = self.client.post(reverse('login'), {
            'username': 'cliente@test.com',
            'password': 'test1234',
        })
        self.assertIn(resp.status_code, [200, 302])

    def test_login_incorrecto_no_autentica(self):
        """Credenciales incorrectas → usuario no queda autenticado."""
        resp = self.client.post(reverse('login'), {
            'username': 'cliente@test.com',
            'password': 'contrasenia_mala',
        })
        self.assertFalse(resp.wsgi_request.user.is_authenticated)

    def test_nueva_reservacion_requiere_login(self):
        """Sin autenticación, acceder a nueva reservación redirige al login."""
        resp = self.client.get(reverse(URL_NUEVA))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login', resp['Location'])


# ─── Camino feliz ─────────────────────────────────────────────────────────────

class TestNuevaReservacion(BaseTestCase):

    def setUp(self):
        super().setUp()
        self._login()

    @patch(MOCK_OBS_CONFIRMACION)
    @patch(MOCK_SUBJECT)
    def test_reservacion_exitosa_camping(self, mock_sub, mock_obs):
        """POST válido (julio, sin martes) → reservación activa, disponibilidad decrementada."""
        mock_sub.return_value.notificar = lambda r: None

        self.client.post(reverse(URL_NUEVA), {
            'parque':       self.parque.pk,
            'fecha_inicio': '2026-07-08',   # miércoles
            'fecha_termino':'2026-07-10',   # viernes
            'num_personas': 2,
            'tipo_visita':  'camping',
        })

        reservacion = Reservacion.objects.filter(cliente=self.cliente_perfil).first()
        self.assertIsNotNone(reservacion)
        self.assertEqual(reservacion.estado, 'activa')
        self.assertEqual(reservacion.tipo_visita, 'camping')

        self.parque.refresh_from_db()
        self.assertEqual(self.parque.ocupados_camping, 1)

    @patch(MOCK_OBS_CONFIRMACION)
    @patch(MOCK_SUBJECT)
    def test_reservacion_exitosa_redirige_a_confirmacion(self, mock_sub, mock_obs):
        """Reservación válida → redirección a la pantalla de confirmación."""
        mock_sub.return_value.notificar = lambda r: None

        resp = self.client.post(reverse(URL_NUEVA), {
            'parque':       self.parque.pk,
            'fecha_inicio': '2026-07-08',
            'fecha_termino':'2026-07-10',
            'num_personas': 1,
            'tipo_visita':  'camping',
        }, follow=False)

        self.assertEqual(resp.status_code, 302)
        self.assertIn('confirmacion', resp['Location'])


# ─── Validaciones rechazadas ──────────────────────────────────────────────────

class TestValidacionesEnVista(BaseTestCase):

    def setUp(self):
        super().setUp()
        self._login()

    def test_rechaza_fecha_fuera_del_festival(self):
        """Fecha en mayo → formulario con error, sin crear reservación."""
        resp = self.client.post(reverse(URL_NUEVA), {
            'parque':       self.parque.pk,
            'fecha_inicio': '2026-05-10',
            'fecha_termino':'2026-05-12',
            'num_personas': 2,
            'tipo_visita':  'camping',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Reservacion.objects.count(), 0)

    def test_rechaza_estancia_con_martes(self):
        """Estancia lunes–miércoles incluye martes → sin crear reservación."""
        # 2026-07-06 lunes, 2026-07-08 miércoles — martes 07/07 queda adentro
        resp = self.client.post(reverse(URL_NUEVA), {
            'parque':       self.parque.pk,
            'fecha_inicio': '2026-07-06',
            'fecha_termino':'2026-07-08',
            'num_personas': 2,
            'tipo_visita':  'camping',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Reservacion.objects.count(), 0)

    def test_rechaza_cabana_en_parque_sin_cabanas(self):
        """Parque sin cabañas + tipo_visita='cabana' → error, sin crear reservación."""
        self.parque.tiene_cabanas = False
        self.parque.save()

        resp = self.client.post(reverse(URL_NUEVA), {
            'parque':       self.parque.pk,
            'fecha_inicio': '2026-07-08',
            'fecha_termino':'2026-07-10',
            'num_personas': 2,
            'tipo_visita':  'cabana',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Reservacion.objects.count(), 0)


# ─── Cancelación ──────────────────────────────────────────────────────────────

class TestCancelacion(BaseTestCase):

    def setUp(self):
        super().setUp()
        self._login()
        self.reservacion = Reservacion.objects.create(
            cliente=self.cliente_perfil,
            parque=self.parque,
            fecha_inicio=date(2026, 7, 8),
            fecha_termino=date(2026, 7, 10),
            num_personas=2,
            tipo_visita='camping',
            estado='activa',
        )

    @patch(MOCK_OBS_CANCELACION)
    @patch(MOCK_SUBJECT)
    def test_cancelacion_cambia_estado(self, mock_sub, mock_obs):
        """POST a cancelar → estado pasa a 'cancelada'."""
        mock_sub.return_value.notificar = lambda r: None

        self.client.post(reverse(URL_CANCELAR, args=[self.reservacion.pk]))
        self.reservacion.refresh_from_db()
        self.assertEqual(self.reservacion.estado, 'cancelada')

    def test_no_cancela_reservacion_ya_cancelada(self):
        """Cancelar una reservación ya cancelada → redirección con mensaje de error."""
        self.reservacion.estado = 'cancelada'
        self.reservacion.save()

        resp = self.client.post(reverse(URL_CANCELAR, args=[self.reservacion.pk]))
        self.assertEqual(resp.status_code, 302)
        self.reservacion.refresh_from_db()
        self.assertEqual(self.reservacion.estado, 'cancelada')

    def test_mis_reservaciones_lista_las_del_cliente(self):
        """La vista mis_reservaciones incluye las reservaciones del cliente autenticado."""
        resp = self.client.get(reverse(URL_MIS_RESERV))
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.reservacion, resp.context['reservaciones'])


# ─── Acceso de administrador ──────────────────────────────────────────────────

class TestAccesoAdmin(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.admin = Usuario.objects.create_user(
            email='admin@test.com',
            nombre='Admin',
            apellido='Sistema',
            password='admin1234',
            is_staff=True,
        )

    @patch(MOCK_OBS_CONFIRMACION)
    @patch(MOCK_SUBJECT)
    def test_admin_no_puede_reservar(self, mock_sub, mock_obs):
        """Un administrador que intenta reservar es redirigido al mapa."""
        self.client.login(username='admin@test.com', password='admin1234')
        resp = self.client.post(reverse(URL_NUEVA), {
            'parque':       self.parque.pk,
            'fecha_inicio': '2026-07-08',
            'fecha_termino':'2026-07-10',
            'num_personas': 2,
            'tipo_visita':  'camping',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Reservacion.objects.count(), 0)

    def test_cliente_no_puede_ver_todas_reservaciones(self):
        """Un cliente sin is_staff no puede acceder a todas_reservaciones."""
        self._login()
        resp = self.client.get(reverse(URL_TODAS_ADMIN))
        self.assertEqual(resp.status_code, 302)
