"""
Modelos de reservaciones — MEC Solutions
"""

from django.db import models
from django.conf import settings


class TipoVisita(models.TextChoices):
    CABANA  = 'cabana',  'Cabaña'
    CAMPING = 'camping', 'Camping'


class Reservacion(models.Model):
    """
    Registra una reservación de un cliente en un parque (CU-08).
    El estado puede ser 'activa' o 'cancelada'; las canceladas
    se conservan para historial pero no ocupan capacidad.
    """

    cliente = models.ForeignKey(
        'usuarios.Cliente',
        on_delete=models.CASCADE,
        related_name='reservaciones',
        verbose_name='Cliente',
    )
    parque = models.ForeignKey(
        'parques.Parque',
        on_delete=models.PROTECT,   # No eliminar parques con reservaciones
        related_name='reservaciones',
        verbose_name='Parque',
    )
    fecha_inicio  = models.DateField('Fecha de inicio')
    fecha_termino = models.DateField('Fecha de término')
    num_personas  = models.PositiveIntegerField('Número de personas')
    estado = models.CharField(
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

    def confirmar(self):
        """
        Persiste la reservación como activa y actualiza el contador de
        ocupación del parque.  Al guardar, la señal post_save dispara
        el Observer que envía el correo de confirmación (CU-11).
        """
        self.estado = 'activa'
        self.save()
        self._actualizar_contador_parque()

        from .observers import ReservacionSubject, EmailConfirmacionObserver
        subject = ReservacionSubject()
        subject.agregar_observer(EmailConfirmacionObserver())
        subject.notificar(self)

    def cancelar(self):
        """
        Marca la reservación como cancelada y libera el espacio en el parque.
        Notifica al cliente por correo (Observer).
        """
        self.estado = 'cancelada'
        self.save()
        self._actualizar_contador_parque()

        from .observers import ReservacionSubject, EmailCancelacionObserver
        subject = ReservacionSubject()
        subject.agregar_observer(EmailCancelacionObserver())
        subject.notificar(self)

    def _actualizar_contador_parque(self):
        """Recalcula los ocupados del parque según reservaciones activas."""
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
