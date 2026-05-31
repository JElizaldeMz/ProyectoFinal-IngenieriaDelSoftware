"""
Validación de reservaciones — patrón Strategy + Template Method + Singleton
MEC Solutions
"""

from abc import ABC, abstractmethod
from datetime import date, timedelta
from django.conf import settings


# ─── Base (Template Method) ───────────────────────────────────────────────────

class ValidacionReservacion(ABC):
    """
    Clase base para todas las validaciones.
    Define el esqueleto: primero revisa coherencia de fechas (paso común),
    luego delega la regla específica a cada subclase (_validar_regla).
    """

    def validar(self, reservacion) -> tuple[bool, str]:
        # Precondición común a todas las estrategias
        if reservacion.fecha_inicio > reservacion.fecha_termino:
            return False, 'La fecha de inicio no puede ser mayor que la fecha de término.'
        return self._validar_regla(reservacion)

    @abstractmethod
    def _validar_regla(self, reservacion) -> tuple[bool, str]:
        """Cada estrategia concreta implementa su propia regla de negocio."""
        pass


# ─── Strategy 1: rango del festival ───────────────────────────────────────────

class ValidacionFestival(ValidacionReservacion):
    """
    RNF01 — Las reservaciones solo pueden hacerse dentro del período
    junio–agosto 2026 (meses configurados en settings).
    """

    def _validar_regla(self, reservacion) -> tuple[bool, str]:
        anio = settings.FESTIVAL_ANIO
        inicio_festival = date(anio, settings.FESTIVAL_MES_INICIO, 1)
        fin_festival    = date(anio, settings.FESTIVAL_MES_FIN, 31)

        if reservacion.fecha_inicio < inicio_festival:
            return False, f'La fecha de inicio debe ser posterior al {inicio_festival.strftime("%d/%m/%Y")}.'
        if reservacion.fecha_termino > fin_festival:
            return False, f'La fecha de término no puede exceder el {fin_festival.strftime("%d/%m/%Y")}.'
        return True, ''


# ─── Strategy 2: sin martes ───────────────────────────────────────────────────

class ValidacionSinMartes(ValidacionReservacion):
    """
    RNF02 — Los martes están bloqueados por mantenimiento de parques.
    Itera día a día dentro del rango para detectar cualquier martes incluido.
    """

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


# ─── Strategy 3: disponibilidad con solapamiento de fechas ───────────────────

class ValidacionDisponibilidad(ValidacionReservacion):
    """
    RNF06 — Controla que el parque no supere su capacidad máxima.

    La lógica de solapamiento es: dos estancias se cruzan si
        inicio_existente < fin_nueva  AND  fin_existente > inicio_nueva
    Es decir, cualquier reservación activa que empiece antes de que
    termine la nueva Y termine después de que empiece la nueva compite
    por el mismo espacio.
    """

    def _validar_regla(self, reservacion) -> tuple[bool, str]:
        from apps.reservaciones.models import Reservacion

        parque      = reservacion.parque
        tipo_visita = reservacion.tipo_visita
        fecha_ini   = reservacion.fecha_inicio
        fecha_fin   = reservacion.fecha_termino

        # El parque podría no ofrecer cabañas
        if tipo_visita == 'cabana' and not parque.tiene_cabanas:
            return False, f'El parque {parque.nombre} no cuenta con cabañas.'

        capacidad = parque.cap_cabanas if tipo_visita == 'cabana' else parque.cap_camping

        # Cuántas reservaciones activas se solapan con el rango solicitado
        solapadas = Reservacion.objects.filter(
            parque=parque,
            tipo_visita=tipo_visita,
            estado='activa',
            fecha_inicio__lt=fecha_fin,
            fecha_termino__gt=fecha_ini,
        ).count()

        if solapadas >= capacidad:
            return False, (
                f'El parque {parque.nombre} no tiene lugares disponibles de '
                f'{reservacion.get_tipo_visita_display()} '
                f'para las fechas {fecha_ini.strftime("%d/%m/%Y")} – '
                f'{fecha_fin.strftime("%d/%m/%Y")}. '
                f'Prueba con otras fechas o elige otro parque.'
            )

        return True, ''


# ─── Contexto Singleton ───────────────────────────────────────────────────────

class ValidadorReservaciones:
    """
    Contexto del patrón Strategy.  Ejecuta las tres estrategias en orden
    y se detiene en la primera que falle.

    Es un Singleton: la instancia se crea una sola vez y se reutiliza,
    evitando reinstanciar las estrategias en cada petición.
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
        """Ejecuta todas las estrategias; devuelve (False, mensaje) al primer fallo."""
        for estrategia in self.estrategias:
            valido, mensaje = estrategia.validar(reservacion)
            if not valido:
                return False, mensaje
        return True, ''
