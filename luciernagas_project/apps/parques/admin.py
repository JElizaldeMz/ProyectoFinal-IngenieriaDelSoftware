from django.contrib import admin
from .models import Parque

@admin.register(Parque)
class ParqueAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'direccional', 'tiene_cabanas', 'cap_camping', 'activo']
