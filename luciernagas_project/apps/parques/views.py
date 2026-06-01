"""
Vistas del módulo de parques — MEC Solutions
Patrón Template Method via Class-Based Views (CBV) de Django.
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
    return render(request, 'parques/landing.html')


def mapa(request):
    parques = Parque.objects.filter(activo=True)
    parques_json = json.dumps([
        {
            'id':            p.pk,
            'nombre':        p.nombre,
            'latitud':       p.latitud,
            'longitud':      p.longitud,
            'direccion':     p.direccional,
            'servicios':     p.servicios,
            'horario':       p.horario,
            'tiene_cabanas': p.tiene_cabanas,
        }
        for p in parques
    ])
    return render(request, 'parques/mapa.html', {
        'parques':      parques,
        'parques_json': parques_json,
    })


def detalle_parque(request, pk):
    parque = get_object_or_404(Parque, pk=pk, activo=True)
    disp_camping = parque.cap_camping - parque.ocupados_camping
    disp_cabanas = parque.cap_cabanas - parque.ocupados_cabanas if parque.tiene_cabanas else 0
    return render(request, 'parques/detalle.html', {
        'parque':      parque,
        'disp_camping': disp_camping,
        'disp_cabanas': disp_cabanas,
    })


def parques_json_api(request):
    """
    Endpoint JSON — disponibilidad por fechas.
    Si se pasan fecha_inicio y fecha_termino como GET params,
    calcula disponibilidad considerando solapamiento.
    """
    from apps.reservaciones.models import Reservacion

    fecha_ini_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_termino')

    parques = Parque.objects.filter(activo=True)
    data = {}

    for p in parques:
        # Si hay fechas, calcular solapamiento real
        if fecha_ini_str and fecha_fin_str:
            try:
                from datetime import date
                fi = date.fromisoformat(fecha_ini_str)
                ff = date.fromisoformat(fecha_fin_str)

                ocupados_camping = Reservacion.objects.filter(
                    parque=p, tipo_visita='camping', estado='activa',
                    fecha_inicio__lt=ff, fecha_termino__gt=fi,
                ).count()

                ocupados_cabanas = Reservacion.objects.filter(
                    parque=p, tipo_visita='cabana', estado='activa',
                    fecha_inicio__lt=ff, fecha_termino__gt=fi,
                ).count() if p.tiene_cabanas else 0

            except ValueError:
                ocupados_camping = p.ocupados_camping
                ocupados_cabanas = p.ocupados_cabanas
        else:
            # Sin fechas — usar contadores generales
            ocupados_camping = p.ocupados_camping
            ocupados_cabanas = p.ocupados_cabanas

        data[str(p.pk)] = {
            'tiene_cabanas': p.tiene_cabanas,
            'disp_camping':  max(0, p.cap_camping - ocupados_camping),
            'disp_cabanas':  max(0, p.cap_cabanas - ocupados_cabanas),
        }

    return JsonResponse(data)


# ── Patrón Template Method via CBV ────────────────────────────────────────────

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


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
    """CU-18 — Eliminar parque."""
    model         = Parque
    template_name = 'parques/admin/confirmar_eliminacion.html'
    success_url   = reverse_lazy('parques:lista_admin')


class ParqueListView(AdminRequiredMixin, ListView):
    model               = Parque
    template_name       = 'parques/admin/lista_parques.html'
    context_object_name = 'parques'
