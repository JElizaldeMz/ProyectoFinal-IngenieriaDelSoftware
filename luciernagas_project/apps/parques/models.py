"""
Modelo Parque — MEC Solutions
Atributos del diagrama de clases:
idParque, nombre, direccional, servicios, horario,
latitud, longitud, tieneCabanas, capCamping, capCabanas
"""

from django.db import models


class Parque(models.Model):
    """
    Representa un parque oficial del Festival Internacional de las Luciérnagas 2026.
    El administrador es responsable de crear, editar y eliminar parques (RF03).
    """

    # ── Atributos del diagrama de clases ──────────────────────────────────────
    nombre      = models.CharField('Nombre del parque', max_length=200)
    direccional = models.CharField('Dirección', max_length=300)
    servicios   = models.TextField('Servicios disponibles')
    horario     = models.CharField('Horario de atención', max_length=150)

    # Coordenadas para el mapa interactivo (RF02.1)
    latitud   = models.FloatField('Latitud')
    longitud  = models.FloatField('Longitud')

    # Configuración de hospedaje (RNF03 — todos tienen camping; cabañas es opcional)
    tiene_cabanas = models.BooleanField('¿Tiene cabañas?', default=False)
    cap_camping   = models.PositiveIntegerField('Capacidad máxima camping', default=0)
    cap_cabanas   = models.PositiveIntegerField('Capacidad máxima cabañas', default=0)

    # Control de disponibilidad actual (RNF06)
    ocupados_camping = models.PositiveIntegerField('Lugares camping ocupados', default=0)
    ocupados_cabanas = models.PositiveIntegerField('Lugares cabañas ocupados', default=0)

    activo = models.BooleanField('Parque activo', default=True)

    class Meta:
        verbose_name = 'Parque'
        verbose_name_plural = 'Parques'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def get_disponibilidad(self, tipo_visita):
        """
        Devuelve el número de lugares disponibles según el tipo de visita.
        tipo_visita: 'camping' o 'cabana'
        """
        if tipo_visita == 'cabana':
            return self.cap_cabanas - self.ocupados_cabanas
        return self.cap_camping - self.ocupados_camping

    def tiene_disponibilidad(self, tipo_visita):
        """Verifica si hay al menos un lugar disponible (CU-10)."""
        return self.get_disponibilidad(tipo_visita) > 0
