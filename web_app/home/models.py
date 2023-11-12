from django.db import models

#----------------------------------------------------------------

#----------------------------------------------------------------
class configuraciones_generales(models.Model):
    CONEXION_CHOICES = (
        ('Wi-Fi', 'Wi-Fi'),
        ('Ethernet', 'Ethernet'),
    )
        
    canal_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='ID del Canal de Telegram')
    chat_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='ID del Chat de Telegram')
    message_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='ID del Mensaje de Telegram')
    acces_token_alert = models.CharField(max_length=100, blank=True, null=True, verbose_name='Token del BOT de Alerta')
    acces_token_db = models.CharField(max_length=100, blank=True, null=True, verbose_name='Token del BOT de Guardado')
    host = models.CharField(max_length=100, blank=True, null=True, verbose_name='Host de la Base de Datos')
    usuario = models.CharField(max_length=100, blank=True, null=True, verbose_name='Usuario de la Base de Datos')
    contraseña = models.CharField(max_length=100, blank=True, null=True, verbose_name='Contraseña de la Base de Datos')
    base_de_datos = models.CharField(max_length=100, blank=True, null=True, verbose_name='Nombre de la Base de Datos')
    Interfaz = models.CharField(max_length=100, blank=True, null=True, choices=CONEXION_CHOICES, verbose_name='Interfaz de Red')

    informacion_adicional = models.TextField(blank=True, null=True, verbose_name='Información Adicional')
    
    class Meta:
        verbose_name_plural = "General"
        verbose_name = "General" 

    def __str__(self):
        return "Configuraciones Generales"  

class configuraciones_del_sistema(models.Model):

    CONEXION_CAMARA_CHOICES = (
        ('0', 'Conexión Directa'),
        ('1', 'Cámara IP'),
        ('2', 'Droidcam'),
        ('3', 'Video de Prueba'),
    )

    CONEXION_LOCAL_CAMARA_CHOICES = (
        ('0', 'Cámara 1'),
        ('1', 'Cámara 2'),
        ('2', 'Cámara 4'),
        ('3', 'Cámara 5'),
        ('4', 'Cámara 6'),
        ('5', 'Cámara 7'),
        ('6', 'Cámara 8'),
        ('7', 'Cámara 9'),
        ('8', 'Cámara 10'),
    )

    CONEXION_FPS_CHOICES = (
        ('10', '10'),
        ('15', '15'),
        ('20', '20'),
        ('25', '25'),
        ('30', '30'),
    )

    latitude = models.CharField(max_length=100, blank=True, null=True, verbose_name='Geolocalización: Latitud')
    longitude = models.CharField(max_length=100, blank=True, null=True, verbose_name='Geolocalización: Longitud')
    camera_option = models.CharField(max_length=100, blank=True, null=True, choices=CONEXION_CAMARA_CHOICES, verbose_name='Tipo de Cámara')
    ip_camera_address = models.CharField(max_length=100, blank=True, null=True, verbose_name='IP de la Cámara')  
    local_camara = models.CharField(max_length=100, blank=True, null=True, choices=CONEXION_LOCAL_CAMARA_CHOICES, verbose_name='Número de Cámara Local')
    camara_fps = models.CharField(max_length=100, blank=True, null=True, choices=CONEXION_FPS_CHOICES, verbose_name='Frames por Segundo de la Cámara')
    max_frames = models.CharField(max_length=100, blank=True, null=True, verbose_name='Número de Frames que se van a Procesar')

    informacion_adicional = models.TextField(blank=True, null=True, verbose_name='Información Adicional')
    
    class Meta:
        verbose_name_plural = "Sistema"
        verbose_name = "Sistema"  

    def __str__(self):
        return "Configuraciones del Sistema"  