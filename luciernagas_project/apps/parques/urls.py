"""URLs del módulo de parques — MEC Solutions"""
from django.urls import path
from . import views

app_name = 'parques'

urlpatterns = [
    # Landing page (raíz del sitio)
    path('', views.landing, name='landing'),

    # CU-01 / CU-06 — Mapa interactivo con todos los parques
    path('mapa/', views.mapa, name='mapa'),

    # CU-02 / CU-07 — Detalle de un parque (info al hacer clic en el pin)
    path('<int:pk>/', views.detalle_parque, name='detalle'),

    # ── Admin: gestión de parques ─────────────────────────────────────────────
    # CU-16 — Crear parque
    path('admin/crear/', views.ParqueCreateView.as_view(), name='crear'),

    # CU-17 — Editar parque
    path('admin/<int:pk>/editar/', views.ParqueUpdateView.as_view(), name='editar'),

    # CU-18 — Eliminar parque
    path('admin/<int:pk>/eliminar/', views.ParqueDeleteView.as_view(), name='eliminar'),

    # Listar todos los parques (panel admin)
    path('admin/lista/', views.ParqueListView.as_view(), name='lista_admin'),
]
