"""
Patrón Strategy + Template Method + Singleton — Validación de reservaciones
MEC Solutions
"""

from abc import ABC, abstractmethod
from datetime import date, timedelta
from django.conf import settings


# ── Template Method ───────────────────────────────────────────────────────────
class ValidacionReservacion(ABC):
    """Clase base — Template Method."""

    def validar(self, reservacion) -> tuple[bool, str]:
        if reservacion.fecha_inicio > reservacion.fecha_termino:
            return False, 'La fecha de inicio no puede ser mayor que la fecha de término.'
        return self._validar_regla(reservacion)

    @abstractmethod
    def _validar_regla(self, reservacion) -> tuple[bool, str]:
        pass


# ── Strategy 1 ────────────────────────────────────────────────────────────────
class ValidacionFestival(ValidacionReservacion):
    """RNF01 — Solo fechas dentro de junio–agosto 2026."""

    def _validar_regla(self, reservacion) -> tuple[bool, str]:
        anio = settings.FESTIVAL_ANIO
        inicio_festival = date(anio, settings.FESTIVAL_MES_INICIO, 1)
        fin_festival    = date(anio, settings.FESTIVAL_MES_FIN, 31)

        if reservacion.fecha_inicio < inicio_festival:
            return False, f'La fecha de inicio debe ser posterior al {inicio_festival.strftime("%d/%m/%Y")}.'
        if reservacion.fecha_termino > fin_festival:
            return False, f'La fecha de término no puede exceder el {fin_festival.strftime("%d/%m/%Y")}.'
        return True, ''


# ── Strategy 2 ────────────────────────────────────────────────────────────────
class ValidacionSinMartes(ValidacionReservacion):
    """RNF02 — No se permiten reservaciones que incluyan martes."""

    def _validar_regla(self, reservacion) -> tuple[bool, str]:
        fecha_actual = reservacion.fecha_inicio
        while fecha_actual <= reservacion.fecha_termino:
            if fecha_actual.weekday() == settings.DIA_MANTENIMIENTO:
                return False, (
                    f'La estancia incluye el martes {fecha_actual.strftime("%d/%m/%Y")}, '
                    f'día de mantenimiento.'
                )
            fecha_actual += timedelta(days=1)
        return True, ''


# ── Strategy 3 — Disponibilidad por fechas ───────────────────────────────────
class ValidacionDisponibilidad(ValidacionReservacion):
    """
    RNF06 — Verifica disponibilidad considerando solapamiento de fechas.

    Dos reservaciones se solapan si:
        inicio_A < termino_B  AND  termino_A > inicio_A
    Es decir, la nueva reservación compite con cualquier reservación activa
    cuyas fechas se crucen con las fechas solicitadas.
    """

    def _validar_regla(self, reservacion) -> tuple[bool, str]:
        from apps.reservaciones.models import Reservacion

        parque      = reservacion.parque
        tipo_visita = reservacion.tipo_visita
        fecha_ini   = reservacion.fecha_inicio
        fecha_fin   = reservacion.fecha_termino

        # Verificar que el parque ofrezca ese tipo de hospedaje
        if tipo_visita == 'cabana' and not parque.tiene_cabanas:
            return False, f'El parque {parque.nombre} no cuenta con cabañas.'

        # Capacidad máxima para el tipo solicitado
        if tipo_visita == 'cabana':
            capacidad = parque.cap_cabanas
        else:
            capacidad = parque.cap_camping

        # Contar reservaciones activas que se solapan con las fechas solicitadas
        # Solapamiento: inicio_existente < fecha_fin_nueva AND termino_existente > fecha_ini_nueva
        reservaciones_solapadas = Reservacion.objects.filter(
            parque=parque,
            tipo_visita=tipo_visita,
            estado='activa',
            fecha_inicio__lt=fecha_fin,   # empieza antes de que termine la nueva
            fecha_termino__gt=fecha_ini,  # termina después de que empiece la nueva
        ).count()

        if reservaciones_solapadas >= capacidad:
            return False, (
                f'El parque {parque.nombre} no tiene lugares disponibles de '
                f'{reservacion.get_tipo_visita_display()} '
                f'para las fechas {fecha_ini.strftime("%d/%m/%Y")} – '
                f'{fecha_fin.strftime("%d/%m/%Y")}. '
                f'Prueba con otras fechas o elige otro parque.'
            )

        return True, ''


# ── Singleton + Context ───────────────────────────────────────────────────────
class ValidadorReservaciones:
    """
    Contexto del patrón Strategy.
    Singleton: una única instancia global con las estrategias ya cargadas.
    """

    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia.estrategias = [
                ValidacionFestival(),
                ValidacionSinMartes(),
                ValidacionDisponibilidad(),
            ]
        return cls._instancia

    def validar(self, reservacion) -> tuple[bool, str]:
        for estrategia in self.estrategias:
            valido, mensaje = estrategia.validar(reservacion)
            if not valido:
                return False, mensaje
        return True, ''
