"""
Vistas del módulo de parques — MEC Solutions
Patrón Template Method via Class-Based Views (CBV) de Django.
CU-01/06 Mapa | CU-02/07 Detalle | CU-16 Crear | CU-17 Editar | CU-18 Eliminar
"""

import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy
from django.http import JsonResponse

from .models import Parque
from .forms import ParqueForm


def landing(request):
    """Landing page — página principal del festival."""
    return render(request, 'parques/landing.html')


def mapa(request):
    """
    CU-01 / CU-06 — Mapa interactivo con todos los parques oficiales (RF02.1).
    Pasa los datos de parques como JSON para Leaflet.js.
    """
    parques = Parque.objects.filter(activo=True)
    parques_json = json.dumps([
        {
            'id':        p.pk,
            'nombre':    p.nombre,
            'latitud':   p.latitud,
            'longitud':  p.longitud,
            'direccion': p.direccional,
            'servicios': p.servicios,
            'horario':   p.horario,
            'tiene_cabanas': p.tiene_cabanas,
        }
        for p in parques
    ])
    return render(request, 'parques/mapa.html', {
        'parques':      parques,
        'parques_json': parques_json,
    })


def detalle_parque(request, pk):
    """
    CU-02 / CU-07 — Información del parque al hacer clic en el marcador (RF02.2).
    """
    parque = get_object_or_404(Parque, pk=pk, activo=True)
    return render(request, 'parques/detalle.html', {'parque': parque})


# ── Vistas CRUD para administradores (Patrón Template Method) ─────────────────

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin que restringe el acceso exclusivamente a administradores."""

    def test_func(self):
        return hasattr(self.request.user, 'administrador')


class ParqueCreateView(AdminRequiredMixin, CreateView):
    """CU-16 — Crear parque."""
    model         = Parque
    form_class    = ParqueForm
    template_name = 'parques/admin/form_parque.html'
    success_url   = reverse_lazy('parques:lista_admin')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Crear nuevo parque'
        ctx['accion'] = 'Guardar parque'
        return ctx


class ParqueUpdateView(AdminRequiredMixin, UpdateView):
    """CU-17 — Editar parque."""
    model         = Parque
    form_class    = ParqueForm
    template_name = 'parques/admin/form_parque.html'
    success_url   = reverse_lazy('parques:lista_admin')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar parque: {self.object.nombre}'
        ctx['accion'] = 'Guardar cambios'
        return ctx


class ParqueDeleteView(AdminRequiredMixin, DeleteView):
    """CU-18 — Eliminar parque (con confirmación CU-19)."""
    model         = Parque
    template_name = 'parques/admin/confirmar_eliminacion.html'
    success_url   = reverse_lazy('parques:lista_admin')


class ParqueListView(AdminRequiredMixin, ListView):
    """Listado de parques en el panel de administrador."""
    model         = Parque
    template_name = 'parques/admin/lista_parques.html'
    context_object_name = 'parques'
