from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'usuarios'

urlpatterns = [
    # CU-03 — Registro
    path('registro/', views.registro, name='registro'),

    # Login/logout usando las vistas de Django (igual que práctica 8)
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Dashboard del cliente
    path('dashboard/', views.dashboard_cliente, name='dashboard'),
]
