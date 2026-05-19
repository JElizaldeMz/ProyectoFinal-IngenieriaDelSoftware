from django.contrib import admin
from .models import Reservacion

@admin.register(Reservacion)
class ReservacionAdmin(admin.ModelAdmin):
    list_display = ['pk', 'cliente', 'parque', 'fecha_inicio', 'fecha_termino', 'tipo_visita', 'estado']
