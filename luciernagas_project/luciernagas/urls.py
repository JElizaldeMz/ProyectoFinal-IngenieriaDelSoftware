from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.parques import views as parques_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    # Landing en la raíz
    path('', parques_views.landing, name='landing_root'),

    # Parques con prefijo /parques/
    path('parques/', include('apps.parques.urls')),
    path('usuarios/', include('apps.usuarios.urls')),
    path('reservaciones/', include('apps.reservaciones.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
