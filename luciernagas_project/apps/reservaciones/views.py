"""
Vistas del módulo de reservaciones — MEC Solutions
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.parques.models import Parque
from apps.usuarios.models import Cliente
from .models import Reservacion
from .forms import ReservacionForm
from .validaciones import ValidadorReservaciones


def _get_or_create_cliente(user):
    cliente, _ = Cliente.objects.get_or_create(usuario=user)
    return cliente


@login_required
def nueva_reservacion(request):
    """CU-08 — Realizar reservación."""

    if hasattr(request.user, 'administrador') or request.user.is_staff:
        messages.error(request, 'Los administradores no pueden realizar reservaciones.')
        return redirect('parques:mapa')

    cliente = _get_or_create_cliente(request.user)
    parque_id = request.GET.get('parque')
    parque_inicial = Parque.objects.filter(pk=parque_id, activo=True).first() if parque_id else None

    if request.method == 'POST':
        form = ReservacionForm(request.POST, usuario=request.user)
        if form.is_valid():
            reservacion = form.save(commit=False)
            reservacion.cliente = cliente

            # ── Singleton: una sola instancia del validador ───────────────────
            validador = ValidadorReservaciones()
            valido, mensaje = validador.validar(reservacion)

            if not valido:
                form.add_error(None, mensaje)
            else:
                # confirmar() dispara el Observer internamente
                reservacion.confirmar()
                messages.success(request, '¡Reservación realizada exitosamente!')
                return redirect('reservaciones:confirmacion', pk=reservacion.pk)
    else:
        initial = {'parque': parque_inicial} if parque_inicial else {}
        form = ReservacionForm(usuario=request.user, initial=initial)

    return render(request, 'reservaciones/nueva_reservacion.html', {
        'form': form,
        'parque_inicial': parque_inicial,
    })


@login_required
def confirmacion(request, pk):
    cliente = _get_or_create_cliente(request.user)
    reservacion = get_object_or_404(Reservacion, pk=pk, cliente=cliente)
    return render(request, 'reservaciones/confirmacion.html', {'reservacion': reservacion})


@login_required
def mis_reservaciones(request):
    cliente = _get_or_create_cliente(request.user)
    reservaciones = cliente.reservaciones.all().order_by('-fecha_creacion')
    return render(request, 'reservaciones/mis_reservaciones.html', {'reservaciones': reservaciones})


@login_required
def cancelar_reservacion(request, pk):
    cliente = _get_or_create_cliente(request.user)
    reservacion = get_object_or_404(Reservacion, pk=pk, cliente=cliente, estado='activa')
    if request.method == 'POST':
        reservacion.cancelar()
        messages.success(request, 'Tu reservación fue cancelada exitosamente.')
        return redirect('reservaciones:mis_reservaciones')
    return render(request, 'reservaciones/confirmar_cancelacion.html', {'reservacion': reservacion})


@login_required
def todas_reservaciones(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('parques:mapa')
    reservaciones = Reservacion.objects.select_related(
        'cliente__usuario', 'parque'
    ).all().order_by('-fecha_creacion')
    return render(request, 'reservaciones/admin/todas_reservaciones.html', {'reservaciones': reservaciones})
