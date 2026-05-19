"""
Patrón Strategy — Validación de reservaciones
MEC Solutions

Clases:
  - ValidacionReservacion (interfaz/base)
  - ValidacionFestival    (RNF01 — fechas jun–ago 2026)
  - ValidacionSinMartes   (RNF02 — sin días martes)
  - ValidacionDisponibilidad (RNF06 — capacidad del parque)

Uso en la vista:
    estrategias = [ValidacionFestival(), ValidacionSinMartes(), ValidacionDisponibilidad()]
    for estrategia in estrategias:
        valido, mensaje = estrategia.validar(reservacion)
        if not valido:
            # mostrar error al usuario
            break
"""

from datetime import date, timedelta
from django.conf import settings


class ValidacionReservacion:
    """Interfaz base para todas las estrategias de validación."""

    def validar(self, reservacion) -> tuple[bool, str]:
        """
        Devuelve (True, '') si la reservación es válida,
        o (False, 'mensaje de error') si no lo es.
        """
        raise NotImplementedError("Las subclases deben implementar validar()")


class ValidacionFestival(ValidacionReservacion):
    """
    RNF01 — Las reservaciones solo pueden realizarse para fechas
    dentro de los meses de junio, julio y agosto de 2026.
    """

    def validar(self, reservacion) -> tuple[bool, str]:
        anio    = settings.FESTIVAL_ANIO
        mes_ini = settings.FESTIVAL_MES_INICIO
        mes_fin = settings.FESTIVAL_MES_FIN

        inicio_festival  = date(anio, mes_ini, 1)
        # Último día de agosto
        fin_festival     = date(anio, mes_fin, 31)

        if reservacion.fecha_inicio < inicio_festival:
            return False, (
                f'La fecha de inicio debe ser a partir del '
                f'{inicio_festival.strftime("%d/%m/%Y")} (inicio del festival).'
            )
        if reservacion.fecha_termino > fin_festival:
            return False, (
                f'La fecha de término no puede ser después del '
                f'{fin_festival.strftime("%d/%m/%Y")} (fin del festival).'
            )
        if reservacion.fecha_inicio > reservacion.fecha_termino:
            return False, 'La fecha de inicio no puede ser mayor que la fecha de término.'

        return True, ''


class ValidacionSinMartes(ValidacionReservacion):
    """
    RNF02 — El sistema no permitirá reservaciones que incluyan días martes,
    ya que ese día se realiza mantenimiento en los parques.
    """

    def validar(self, reservacion) -> tuple[bool, str]:
        dia_mantenimiento = settings.DIA_MANTENIMIENTO  # 1 = martes

        fecha_actual = reservacion.fecha_inicio
        while fecha_actual <= reservacion.fecha_termino:
            if fecha_actual.weekday() == dia_mantenimiento:
                return False, (
                    f'La estancia incluye el martes {fecha_actual.strftime("%d/%m/%Y")}, '
                    f'día de mantenimiento. Por favor elige otras fechas.'
                )
            fecha_actual += timedelta(days=1)

        return True, ''


class ValidacionDisponibilidad(ValidacionReservacion):
    """
    RNF06 — El sistema controlará la capacidad máxima de hospedaje
    por parque, bloqueando reservaciones cuando se alcance el límite.
    """

    def validar(self, reservacion) -> tuple[bool, str]:
        parque      = reservacion.parque
        tipo_visita = reservacion.tipo_visita

        # Verificar que el parque ofrezca ese tipo de hospedaje
        if tipo_visita == 'cabana' and not parque.tiene_cabanas:
            return False, (
                f'El parque {parque.nombre} no cuenta con cabañas. '
                f'Solo está disponible la opción de camping.'
            )

        if not parque.tiene_disponibilidad(tipo_visita):
            return False, (
                f'El parque {parque.nombre} no tiene lugares disponibles '
                f'de tipo "{reservacion.get_tipo_visita_display()}" para las fechas seleccionadas.'
            )

        return True, ''
