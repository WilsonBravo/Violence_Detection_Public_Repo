from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "home"
    icon = 'fa fa-cog'
    verbose_name = 'Configuración'  # Cambia el nombre aquí
