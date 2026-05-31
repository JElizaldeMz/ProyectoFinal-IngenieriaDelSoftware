"""
Pruebas de unidad — Modelo Parque
MEC Solutions

Cubren get_disponibilidad, tiene_disponibilidad y la lógica de cabañas opcionales.

Ejecutar:
    python manage.py test apps.parques.tests.test_models -v 2
"""

from django.test import TestCase
from apps.parques.models import Parque


class TestParqueDisponibilidad(TestCase):

    def _parque(self, cap_camping=10, cap_cabanas=5, tiene_cabanas=True,
                ocupados_camping=0, ocupados_cabanas=0):
        return Parque(
            nombre='Parque Test',
            direccional='Tlaxcala, México',
            servicios='Baños, estacionamiento',
            horario='18:00 – 23:00',
            latitud=19.3,
            longitud=-98.2,
            tiene_cabanas=tiene_cabanas,
            cap_camping=cap_camping,
            cap_cabanas=cap_cabanas,
            ocupados_camping=ocupados_camping,
            ocupados_cabanas=ocupados_cabanas,
        )

    # ── get_disponibilidad ────────────────────────────────────────────────────

    def test_disponibilidad_camping_sin_ocupados(self):
        """10 plazas, 0 ocupadas → 10 disponibles."""
        p = self._parque(cap_camping=10, ocupados_camping=0)
        self.assertEqual(p.get_disponibilidad('camping'), 10)

    def test_disponibilidad_camping_parcialmente_ocupado(self):
        """10 plazas, 6 ocupadas → 4 disponibles."""
        p = self._parque(cap_camping=10, ocupados_camping=6)
        self.assertEqual(p.get_disponibilidad('camping'), 4)

    def test_disponibilidad_camping_lleno(self):
        """10 plazas, 10 ocupadas → 0 disponibles."""
        p = self._parque(cap_camping=10, ocupados_camping=10)
        self.assertEqual(p.get_disponibilidad('camping'), 0)

    def test_disponibilidad_cabanas_correcta(self):
        """5 cabañas, 2 ocupadas → 3 disponibles."""
        p = self._parque(cap_cabanas=5, ocupados_cabanas=2)
        self.assertEqual(p.get_disponibilidad('cabana'), 3)

    # ── tiene_disponibilidad ──────────────────────────────────────────────────

    def test_tiene_disponibilidad_camping_con_lugares(self):
        p = self._parque(cap_camping=5, ocupados_camping=3)
        self.assertTrue(p.tiene_disponibilidad('camping'))

    def test_no_tiene_disponibilidad_camping_lleno(self):
        p = self._parque(cap_camping=5, ocupados_camping=5)
        self.assertFalse(p.tiene_disponibilidad('camping'))

    def test_tiene_disponibilidad_cabana_con_lugares(self):
        p = self._parque(cap_cabanas=3, ocupados_cabanas=1)
        self.assertTrue(p.tiene_disponibilidad('cabana'))

    def test_parque_sin_cabanas_capacidad_cero(self):
        """Parque sin cabañas: cap_cabanas=0, ocupados=0 → get_disponibilidad devuelve 0."""
        p = self._parque(tiene_cabanas=False, cap_cabanas=0, ocupados_cabanas=0)
        self.assertEqual(p.get_disponibilidad('cabana'), 0)
        self.assertFalse(p.tiene_disponibilidad('cabana'))

    # ── __str__ ───────────────────────────────────────────────────────────────

    def test_str_devuelve_nombre(self):
        p = self._parque()
        p.nombre = 'Bosque de Nanacamilpa'
        self.assertEqual(str(p), 'Bosque de Nanacamilpa')
