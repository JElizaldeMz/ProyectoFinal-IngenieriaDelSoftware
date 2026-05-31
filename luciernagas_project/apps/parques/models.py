"""
Modelo Parque — MEC Solutions
Representa un sitio oficial del Festival Internacional de las Luciérnagas 2026.
"""

from django.db import models


class Parque(models.Model):
    """
    Parque participante en el festival.  El administrador gestiona el catálogo
    completo: crear, editar, eliminar (RF03) y configurar capacidad (RNF06).

    Todos los parques tienen zona de camping; las cabañas son opcionales
    y se habilitan con tiene_cabanas=True (RNF03).
    """

    nombre      = models.CharField('Nombre del parque', max_length=200)
    direccional = models.CharField('Dirección', max_length=300)
    servicios   = models.TextField('Servicios disponibles')
    horario     = models.CharField('Horario de atención', max_length=150)

    # Coordenadas para el mapa interactivo (RF02.1)
    latitud  = models.FloatField('Latitud')
    longitud = models.FloatField('Longitud')

    # Configuración de hospedaje (RNF03)
    tiene_cabanas = models.BooleanField('¿Tiene cabañas?', default=False)
    cap_camping   = models.PositiveIntegerField('Capacidad máxima camping', default=0)
    cap_cabanas   = models.PositiveIntegerField('Capacidad máxima cabañas', default=0)

    # Contadores de ocupación actuales (se recalculan en Reservacion.confirmar/cancelar)
    ocupados_camping = models.PositiveIntegerField('Lugares camping ocupados', default=0)
    ocupados_cabanas = models.PositiveIntegerField('Lugares cabañas ocupados', default=0)

    activo = models.BooleanField('Parque activo', default=True)

    class Meta:
        verbose_name = 'Parque'
        verbose_name_plural = 'Parques'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def get_disponibilidad(self, tipo_visita: str) -> int:
        """
        Devuelve lugares disponibles para el tipo_visita dado.
        Retorna 0 si el parque no admite el tipo solicitado.
        """
        if tipo_visita == 'cabana':
            return self.cap_cabanas - self.ocupados_cabanas
        return self.cap_camping - self.ocupados_camping

    def tiene_disponibilidad(self, tipo_visita: str) -> bool:
        """True si hay al menos un lugar libre para el tipo_visita (CU-10)."""
        return self.get_disponibilidad(tipo_visita) > 0
