from django.contrib import admin
from .models import Usuario, Cliente, Administrador

admin.site.register(Usuario)
admin.site.register(Cliente)
admin.site.register(Administrador)
