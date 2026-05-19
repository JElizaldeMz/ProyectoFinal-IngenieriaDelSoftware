"""URLs del módulo de reservaciones — MEC Solutions"""
from django.urls import path
from . import views

app_name = 'reservaciones'

urlpatterns = [
    # CU-08 — Realizar reservación
    path('nueva/', views.nueva_reservacion, name='nueva'),

    # CU-11 — Confirmación de reservación (pantalla de éxito)
    path('<int:pk>/confirmacion/', views.confirmacion, name='confirmacion'),

    # CU-12 — Consultar reservaciones activas del cliente
    path('mis-reservaciones/', views.mis_reservaciones, name='mis_reservaciones'),

    # CU-13 — Cancelar reservación
    path('<int:pk>/cancelar/', views.cancelar_reservacion, name='cancelar'),

    # CU-20 — Consultar todas las reservaciones (solo admin)
    path('admin/todas/', views.todas_reservaciones, name='todas_admin'),
]
