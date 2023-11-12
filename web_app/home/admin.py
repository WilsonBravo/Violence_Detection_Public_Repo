from django import forms
from django.contrib import admin
# from django.forms import PasswordInput

from .models import configuraciones_generales
from .models import configuraciones_del_sistema

class ConfiguracionesGeneralesForm(forms.ModelForm):
    class Meta:
        model = configuraciones_generales
        fields = '__all__'
        widgets = {
            'canal_id': forms.PasswordInput(render_value=True),
            'chat_id': forms.PasswordInput(render_value=True),
            'acces_token_alert': forms.PasswordInput(render_value=True),
            'acces_token_db': forms.PasswordInput(render_value=True),
            'contraseña': forms.PasswordInput(render_value=True),
        }

@admin.register(configuraciones_generales)
class ConfiguracionesGeneralesAdmin(admin.ModelAdmin):
    form = ConfiguracionesGeneralesForm

class configuraciones_del_sistema_Admin(admin.ModelAdmin):
    list_display = (
        'camera_option',
        'local_camara',
        'ip_camera_address',
        'max_frames',
        'latitude',
        'longitude',
        'informacion_adicional',
    )

# Registra el modelo con la clase de administración personalizada
# admin.site.register(configuraciones_generales, configuraciones_generales_Admin)
admin.site.register(configuraciones_del_sistema, configuraciones_del_sistema_Admin)