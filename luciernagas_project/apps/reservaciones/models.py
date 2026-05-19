"""
Modelos de reservaciones — MEC Solutions

Implementa:
  - Enumeración TipoVisita (CABANA, CAMPING)
  - Clase Reservacion con todos los atributos del diagrama de clases
  - Señal post_save para envío de correo (Patrón Observer — RF04.1)
  - Clases Strategy de validación (Patrón Strategy — RNF01, RNF02, RNF06)
"""

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string

from apps.parques.models import Parque


# ─── Enumeración TipoVisita (diagrama de clases) ──────────────────────────────
class TipoVisita(models.TextChoices):
    CABANA   = 'cabana',  'Cabaña'
    CAMPING  = 'camping', 'Camping'


# ─── Modelo Reservacion ───────────────────────────────────────────────────────
class Reservacion(models.Model):
    """
    Representa una reservación en el festival.
    Relación con el diagrama de clases:
      Cliente 1 ──realiza──> 0..n Reservacion
      Reservacion 0..n ──pertenece a──> 1 Parque
    """

    # Atributos del diagrama de clases
    cliente       = models.ForeignKey(
        'usuarios.Cliente',
        on_delete=models.CASCADE,
        related_name='reservaciones',
        verbose_name='Cliente',
    )
    parque        = models.ForeignKey(
        Parque,
        on_delete=models.PROTECT,
        related_name='reservaciones',
        verbose_name='Parque',
    )
    fecha_inicio  = models.DateField('Fecha de inicio')
    fecha_termino = models.DateField('Fecha de término')
    num_personas  = models.PositiveIntegerField('Número de personas')
    estado        = models.CharField(
        'Estado',
        max_length=20,
        choices=[('activa', 'Activa'), ('cancelada', 'Cancelada')],
        default='activa',
    )
    tipo_visita   = models.CharField(
        'Tipo de visita',
        max_length=10,
        choices=TipoVisita.choices,
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Reservación'
        verbose_name_plural = 'Reservaciones'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return (f'Reservación #{self.pk} — {self.cliente} '
                f'en {self.parque} [{self.fecha_inicio} → {self.fecha_termino}]')

    def confirmar(self):
        """Registra la reservación y actualiza disponibilidad (paso 9 camino feliz)."""
        self.estado = 'activa'
        self.save()
        # Actualizar disponibilidad del parque
        if self.tipo_visita == TipoVisita.CABANA:
            self.parque.ocupados_cabanas += 1
        else:
            self.parque.ocupados_camping += 1
        self.parque.save()

    def cancelar(self):
        """Cancela la reservación y libera disponibilidad (CU-13)."""
        self.estado = 'cancelada'
        self.save()
        # Liberar lugar en el parque
        if self.tipo_visita == TipoVisita.CABANA:
            self.parque.ocupados_cabanas = max(0, self.parque.ocupados_cabanas - 1)
        else:
            self.parque.ocupados_camping = max(0, self.parque.ocupados_camping - 1)
        self.parque.save()

    def es_fecha_valida(self):
        """Delega a ValidacionFestival y ValidacionSinMartes (Patrón Strategy)."""
        from apps.reservaciones.validaciones import ValidacionFestival, ValidacionSinMartes
        for estrategia in [ValidacionFestival(), ValidacionSinMartes()]:
            valido, mensaje = estrategia.validar(self)
            if not valido:
                return False, mensaje
        return True, ''

    def es_martes(self):
        """Verifica si alguna fecha de la estancia cae en martes (RNF02)."""
        from datetime import timedelta
        fecha_actual = self.fecha_inicio
        while fecha_actual <= self.fecha_termino:
            if fecha_actual.weekday() == settings.DIA_MANTENIMIENTO:
                return True
            fecha_actual += timedelta(days=1)
        return False

    def enviar_correo(self):
        """Llamado por la señal post_save. Envía correo de confirmación (RF04.1)."""
        asunto = f'Confirmación de reservación — Festival Luciérnagas 2026 #{self.pk}'
        mensaje = (
            f'Hola {self.cliente.usuario.get_full_name()},\n\n'
            f'Tu reservación ha sido confirmada con los siguientes datos:\n\n'
            f'  Parque:        {self.parque.nombre}\n'
            f'  Tipo de visita:{self.get_tipo_visita_display()}\n'
            f'  Fecha inicio:  {self.fecha_inicio}\n'
            f'  Fecha término: {self.fecha_termino}\n'
            f'  Personas:      {self.num_personas}\n'
            f'  Estado:        {self.estado}\n\n'
            f'Gracias por participar en el Festival Internacional de las Luciérnagas 2026.\n\n'
            f'— MEC Solutions'
        )
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [self.cliente.usuario.email],
            fail_silently=True,
        )


# ─── Patrón Observer: señal post_save ─────────────────────────────────────────
@receiver(post_save, sender=Reservacion)
def enviar_correo_confirmacion(sender, instance, created, **kwargs):
    """
    Observer suscrito a Reservacion.post_save.
    Solo envía correo cuando la reservación se crea con estado 'activa'.
    """
    if created and instance.estado == 'activa':
        instance.enviar_correo()
