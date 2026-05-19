"""
Vistas del módulo de usuarios — MEC Solutions
CU-03 Registrarse | CU-04 Login | CU-05 Logout | Dashboard cliente
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Usuario, Cliente
from .forms import RegistroClienteForm


def registro(request):
    """CU-03 — Registrarse en la plataforma (RF01.1)."""
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            # Crear el perfil Cliente asociado
            Cliente.objects.create(usuario=usuario)
            # Iniciar sesión automáticamente al registrarse
            login(request, usuario)
            messages.success(request, f'¡Bienvenido/a, {usuario.nombre}! Tu cuenta fue creada exitosamente.')
            return redirect('parques:mapa')
    else:
        form = RegistroClienteForm()

    return render(request, 'registration/registro.html', {'form': form})


@login_required
def dashboard_cliente(request):
    """Dashboard principal del cliente post-login."""
    try:
        cliente = request.user.cliente
        reservaciones_activas = cliente.ver_reservaciones()
    except Cliente.DoesNotExist:
        reservaciones_activas = []

    return render(request, 'usuarios/dashboard.html', {
        'reservaciones_activas': reservaciones_activas,
    })
