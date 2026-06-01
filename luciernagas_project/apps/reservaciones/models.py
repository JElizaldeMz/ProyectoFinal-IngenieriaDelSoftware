"""
Modelos de reservaciones — MEC Solutions
"""

from django.db import models
from django.conf import settings


class TipoVisita(models.TextChoices):
    CABANA  = 'cabana',  'Cabaña'
    CAMPING = 'camping', 'Camping'


class Reservacion(models.Model):

    cliente = models.ForeignKey(
        'usuarios.Cliente',
        on_delete=models.CASCADE,
        related_name='reservaciones',
        verbose_name='Cliente',
    )
    parque = models.ForeignKey(
        'parques.Parque',
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
    tipo_visita = models.CharField(
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
        return f'Reservación #{self.pk} — {self.cliente} en {self.parque}'

    # ── Refactorización: método privado extraído (DRY) ────────────────────────
    def _actualizar_contadores(self):
        """
        Recalcula y persiste los contadores de ocupación del parque
        para el tipo de visita de esta reservación.

        Extraído de confirmar() y cancelar() para eliminar duplicación
        (mismo bloque de 12 líneas existía en los dos métodos).
        """
        if self.tipo_visita == TipoVisita.CABANA:
            self.parque.ocupados_cabanas = Reservacion.objects.filter(
                parque=self.parque,
                tipo_visita=TipoVisita.CABANA,
                estado='activa',
            ).count()
        else:
            self.parque.ocupados_camping = Reservacion.objects.filter(
                parque=self.parque,
                tipo_visita=TipoVisita.CAMPING,
                estado='activa',
            ).count()
        self.parque.save()

    def confirmar(self):
        """Guarda la reservación como activa y notifica al cliente (Observer)."""
        self.estado = 'activa'
        self.save()
        self._actualizar_contadores()

        from .observers import ReservacionSubject, EmailConfirmacionObserver
        subject = ReservacionSubject()
        subject.agregar_observer(EmailConfirmacionObserver())
        subject.notificar(self)

    def cancelar(self):
        """Cancela la reservación y libera disponibilidad en el parque (Observer)."""
        self.estado = 'cancelada'
        self.save()
        self._actualizar_contadores()

        from .observers import ReservacionSubject, EmailCancelacionObserver
        subject = ReservacionSubject()
        subject.agregar_observer(EmailCancelacionObserver())
        subject.notificar(self)
