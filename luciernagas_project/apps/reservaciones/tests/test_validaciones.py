"""
Pruebas de unidad — Módulo de validaciones de reservaciones
MEC Solutions

Cubren las tres estrategias del patrón Strategy más el contexto Singleton.
No requieren base de datos: se usan objetos simples (SimpleNamespace) para
simular una Reservacion sin tocar el ORM.

Ejecutar:
    python manage.py test apps.reservaciones.tests.test_validaciones -v 2
"""

from datetime import date
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

from django.test import TestCase, override_settings

from apps.reservaciones.validaciones import (
    ValidacionFestival,
    ValidacionSinMartes,
    ValidacionDisponibilidad,
    ValidadorReservaciones,
)


# ─── Configuración del festival para las pruebas ─────────────────────────────
SETTINGS_FESTIVAL = dict(
    FESTIVAL_ANIO=2026,
    FESTIVAL_MES_INICIO=6,
    FESTIVAL_MES_FIN=8,
    DIA_MANTENIMIENTO=1,   # 1 = martes (lunes=0, martes=1, …)
)


def _reservacion(fecha_inicio, fecha_termino, tipo_visita='camping', parque=None):
    """Construye un objeto mínimo que imita una Reservacion del ORM."""
    if parque is None:
        parque = SimpleNamespace(
            tiene_cabanas=True,
            cap_camping=10,
            cap_cabanas=5,
            nombre='Parque de prueba',
        )
    return SimpleNamespace(
        fecha_inicio=fecha_inicio,
        fecha_termino=fecha_termino,
        tipo_visita=tipo_visita,
        parque=parque,
        get_tipo_visita_display=lambda: 'Cabaña' if tipo_visita == 'cabana' else 'Camping',
    )


# ─── Pruebas de ValidacionFestival ────────────────────────────────────────────

@override_settings(**SETTINGS_FESTIVAL)
class TestValidacionFestival(TestCase):

    def setUp(self):
        self.v = ValidacionFestival()

    def test_fecha_valida_dentro_del_festival(self):
        """Reservación de 3 noches en pleno julio → debe pasar."""
        r = _reservacion(date(2026, 7, 10), date(2026, 7, 13))
        valido, _ = self.v.validar(r)
        self.assertTrue(valido)

    def test_fecha_inicio_fuera_del_festival_antes(self):
        """Reservación que comienza en mayo (antes del festival) → debe rechazarse."""
        r = _reservacion(date(2026, 5, 30), date(2026, 6, 5))
        valido, mensaje = self.v.validar(r)
        self.assertFalse(valido)
        self.assertIn('01/06/2026', mensaje)

    def test_fecha_termino_fuera_del_festival_despues(self):
        """Reservación que termina en septiembre (después del festival) → debe rechazarse."""
        r = _reservacion(date(2026, 8, 28), date(2026, 9, 3))
        valido, mensaje = self.v.validar(r)
        self.assertFalse(valido)
        self.assertIn('31/08/2026', mensaje)

    def test_fechas_invertidas(self):
        """Fecha inicio mayor que fecha término → la clase base lo intercepta."""
        r = _reservacion(date(2026, 7, 15), date(2026, 7, 10))
        valido, mensaje = self.v.validar(r)
        self.assertFalse(valido)
        self.assertIn('inicio no puede ser mayor', mensaje)

    def test_primer_dia_del_festival(self):
        """1 de junio exacto → debe ser válido."""
        r = _reservacion(date(2026, 6, 1), date(2026, 6, 3))
        valido, _ = self.v.validar(r)
        self.assertTrue(valido)

    def test_ultimo_dia_del_festival(self):
        """31 de agosto exacto → debe ser válido."""
        r = _reservacion(date(2026, 8, 29), date(2026, 8, 31))
        valido, _ = self.v.validar(r)
        self.assertTrue(valido)


# ─── Pruebas de ValidacionSinMartes ──────────────────────────────────────────

@override_settings(**SETTINGS_FESTIVAL)
class TestValidacionSinMartes(TestCase):

    def setUp(self):
        self.v = ValidacionSinMartes()

    def test_estancia_sin_martes(self):
        """Miércoles a viernes — ningún martes incluido → válido."""
        # 2026-07-08 es miércoles, 2026-07-10 es viernes
        r = _reservacion(date(2026, 7, 8), date(2026, 7, 10))
        valido, _ = self.v.validar(r)
        self.assertTrue(valido)

    def test_estancia_que_incluye_un_martes(self):
        """Lunes a miércoles — el martes queda dentro → debe rechazarse."""
        # 2026-07-06 es lunes, 2026-07-08 es miércoles
        r = _reservacion(date(2026, 7, 6), date(2026, 7, 8))
        valido, mensaje = self.v.validar(r)
        self.assertFalse(valido)
        self.assertIn('07/07/2026', mensaje)   # 07/07/2026 es el martes

    def test_estancia_de_un_dia_que_es_martes(self):
        """Check-in y check-out el mismo martes → debe rechazarse."""
        # 2026-07-07 es martes
        r = _reservacion(date(2026, 7, 7), date(2026, 7, 7))
        valido, _ = self.v.validar(r)
        self.assertFalse(valido)

    def test_estancia_larga_con_multiples_martes(self):
        """Estancia de dos semanas — debe detectar el primer martes."""
        r = _reservacion(date(2026, 7, 1), date(2026, 7, 15))
        valido, mensaje = self.v.validar(r)
        self.assertFalse(valido)
        self.assertIn('07/07/2026', mensaje)   # primer martes del rango

    def test_estancia_de_un_solo_dia_sin_martes(self):
        """Un solo día que no es martes → válido."""
        # 2026-07-08 es miércoles
        r = _reservacion(date(2026, 7, 8), date(2026, 7, 8))
        valido, _ = self.v.validar(r)
        self.assertTrue(valido)


# ─── Pruebas de ValidacionDisponibilidad ─────────────────────────────────────

@override_settings(**SETTINGS_FESTIVAL)
class TestValidacionDisponibilidad(TestCase):

    def setUp(self):
        self.v = ValidacionDisponibilidad()

    def _parque(self, tiene_cabanas=True, cap_camping=5, cap_cabanas=3, nombre='Parque Test'):
        return SimpleNamespace(
            pk=1,
            tiene_cabanas=tiene_cabanas,
            cap_camping=cap_camping,
            cap_cabanas=cap_cabanas,
            nombre=nombre,
        )

    @patch('apps.reservaciones.models.Reservacion')
    def test_hay_disponibilidad_camping(self, MockReservacion):
        """2 de 5 lugares ocupados → debe quedar disponibilidad."""
        MockReservacion.objects.filter.return_value.count.return_value = 2
        parque = self._parque(cap_camping=5)
        r = _reservacion(date(2026, 7, 10), date(2026, 7, 12), 'camping', parque)
        valido, _ = self.v.validar(r)
        self.assertTrue(valido)

    @patch('apps.reservaciones.models.Reservacion')
    def test_parque_lleno_camping(self, MockReservacion):
        """5 de 5 lugares ocupados → no debe quedar disponibilidad."""
        MockReservacion.objects.filter.return_value.count.return_value = 5
        parque = self._parque(cap_camping=5)
        r = _reservacion(date(2026, 7, 10), date(2026, 7, 12), 'camping', parque)
        valido, mensaje = self.v.validar(r)
        self.assertFalse(valido)
        self.assertIn('no tiene lugares disponibles', mensaje)

    def test_parque_sin_cabanas_rechaza_tipo_cabana(self):
        """Parque sin cabañas + tipo_visita='cabana' → rechazar sin consultar BD."""
        parque = self._parque(tiene_cabanas=False)
        r = _reservacion(date(2026, 7, 10), date(2026, 7, 12), 'cabana', parque)
        valido, mensaje = self.v.validar(r)
        self.assertFalse(valido)
        self.assertIn('no cuenta con cabañas', mensaje)

    @patch('apps.reservaciones.models.Reservacion')
    def test_primera_reservacion_siempre_pasa(self, MockReservacion):
        """Sin ninguna reservación previa → siempre hay disponibilidad."""
        MockReservacion.objects.filter.return_value.count.return_value = 0
        parque = self._parque(cap_camping=1)
        r = _reservacion(date(2026, 7, 10), date(2026, 7, 12), 'camping', parque)
        valido, _ = self.v.validar(r)
        self.assertTrue(valido)


# ─── Pruebas del Singleton ────────────────────────────────────────────────────

class TestValidadorSingleton(TestCase):

    def test_misma_instancia_en_llamadas_sucesivas(self):
        """ValidadorReservaciones debe devolver siempre la misma instancia."""
        # Reset manual del singleton para que la prueba sea independiente
        ValidadorReservaciones._instancia = None
        v1 = ValidadorReservaciones()
        v2 = ValidadorReservaciones()
        self.assertIs(v1, v2)

    def test_estrategias_cargadas(self):
        """La instancia debe tener exactamente 3 estrategias."""
        ValidadorReservaciones._instancia = None
        v = ValidadorReservaciones()
        self.assertEqual(len(v.estrategias), 3)
        self.assertIsInstance(v.estrategias[0], ValidacionFestival)
        self.assertIsInstance(v.estrategias[1], ValidacionSinMartes)
        self.assertIsInstance(v.estrategias[2], ValidacionDisponibilidad)
