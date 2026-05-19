from django.apps import AppConfig

class ReservacionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.reservaciones'
    verbose_name = 'Reservaciones'

    def ready(self):
        # Registrar las señales (Patrón Observer — post_save de Reservacion)
        import apps.reservaciones.models  # noqa: F401
