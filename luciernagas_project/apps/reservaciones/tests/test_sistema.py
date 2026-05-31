"""
Prueba de sistema — Camino feliz completo CU-08
MEC Solutions

Ejecutar:
    python manage.py test apps.reservaciones.tests.test_sistema -v 2
"""

from datetime import date
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
from django.urls import reverse

from apps.usuarios.models import Usuario, Cliente
from apps.parques.models import Parque
from apps.reservaciones.models import Reservacion

MOCK_SUBJECT          = 'apps.reservaciones.observers.ReservacionSubject'
MOCK_OBS_CONFIRMACION = 'apps.reservaciones.observers.EmailConfirmacionObserver'


class TestSistemaCaminoFeliz(TestCase):
    """
    Reproduce los 11 pasos del camino feliz (CU-08, punto 13 del proyecto).
    Verifica el estado del sistema en cada paso clave.
    """

    def setUp(self):
        self.client = Client()

        self.usuario = Usuario.objects.create_user(
            email='visitante@test.com',
            nombre='Carlos',
            apellido='Mendoza',
            password='festival2026',
        )
        self.cliente_perfil = Cliente.objects.create(usuario=self.usuario)

        self.parque = Parque.objects.create(
            nombre='Bosque de Nanacamilpa',
            direccional='Nanacamilpa de Mariano Arista, Tlaxcala',
            servicios='Guías especializados, baños, estacionamiento',
            horario='19:00 – 23:00',
            latitud=19.435,
            longitud=-98.545,
            tiene_cabanas=True,
            cap_camping=10,
            cap_cabanas=4,
            activo=True,
        )

    @patch(MOCK_OBS_CONFIRMACION)
    @patch(MOCK_SUBJECT)
    def test_flujo_completo_reservacion(self, mock_sub, mock_obs):
        """
        Pasos 1–11 del camino feliz:
        login → mapa → detalle parque → formulario → POST → confirmación
        """
        mock_instance = MagicMock()
        mock_sub.return_value = mock_instance

        # Paso 1: El cliente accede al mapa
        self.client.login(username='visitante@test.com', password='festival2026')
        resp = self.client.get(reverse('parques:mapa'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.parque, resp.context['parques'])

        # Paso 2: Ve el detalle de un parque
        resp = self.client.get(reverse('parques:detalle', args=[self.parque.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['parque'], self.parque)

        # Pasos 3–6: Accede al formulario de reservación
        resp = self.client.get(
            reverse('reservaciones:nueva'),
            {'parque': self.parque.pk},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.context.get('form'))

        # Pasos 7–9: Envía el formulario — julio, sin martes
        resp = self.client.post(reverse('reservaciones:nueva'), {
            'parque':       self.parque.pk,
            'fecha_inicio': '2026-07-08',   # miércoles
            'fecha_termino':'2026-07-10',   # viernes
            'num_personas': 3,
            'tipo_visita':  'camping',
        }, follow=True)

        # Verificar reservación creada correctamente en BD
        reservacion = Reservacion.objects.filter(cliente=self.cliente_perfil).first()
        self.assertIsNotNone(reservacion, 'La reservación no fue creada en la BD.')
        self.assertEqual(reservacion.estado, 'activa')
        self.assertEqual(reservacion.parque, self.parque)
        self.assertEqual(reservacion.num_personas, 3)

        # Paso 9: Disponibilidad del parque decrementada
        self.parque.refresh_from_db()
        self.assertEqual(self.parque.ocupados_camping, 1)

        # Paso 10: El Observer fue llamado para notificar al cliente
        mock_instance.agregar_observer.assert_called_once()
        mock_instance.notificar.assert_called_once_with(reservacion)

        # Paso 11: Pantalla de confirmación mostrada
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'confirmaci', resp.content.lower())

    @patch(MOCK_OBS_CONFIRMACION)
    @patch(MOCK_SUBJECT)
    def test_segunda_reservacion_reduce_disponibilidad(self, mock_sub, mock_obs):
        """
        Dos reservaciones con fechas solapadas sobre el mismo parque
        reducen el contador de disponibilidad correctamente.
        """
        mock_sub.return_value.notificar = lambda r: None

        self.client.login(username='visitante@test.com', password='festival2026')
        for _ in range(2):
            self.client.post(reverse('reservaciones:nueva'), {
                'parque':       self.parque.pk,
                'fecha_inicio': '2026-07-08',
                'fecha_termino':'2026-07-10',
                'num_personas': 1,
                'tipo_visita':  'camping',
            })

        self.parque.refresh_from_db()
        self.assertEqual(Reservacion.objects.filter(estado='activa').count(), 2)
        self.assertEqual(self.parque.ocupados_camping, 2)

    def test_mapa_solo_muestra_parques_activos(self):
        """Un parque con activo=False no debe aparecer en el mapa."""
        parque_inactivo = Parque.objects.create(
            nombre='Parque Cerrado',
            direccional='Puebla, México',
            servicios='N/A',
            horario='N/A',
            latitud=19.0,
            longitud=-98.0,
            activo=False,
        )
        self.client.login(username='visitante@test.com', password='festival2026')
        resp = self.client.get(reverse('parques:mapa'))
        self.assertNotIn(parque_inactivo, resp.context['parques'])
        self.assertIn(self.parque, resp.context['parques'])
