from django.http import HttpResponse
from django.shortcuts import render
from .models import *
from django.core.mail import EmailMessage
from django.views.decorators import gzip
from django.http import StreamingHttpResponse

import threading
import numpy as np
import subprocess
import os

import psutil
import socket
import sqlite3

from django.contrib.admin.views.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

def is_admin(user):
    return user.is_superuser

admin_required = user_passes_test(is_admin, login_url=reverse_lazy('admin:index'))

# Obtén el directorio actual del archivo .py
directorio_actual = os.path.dirname(os.path.abspath(__file__))
path_web_app = os.path.dirname(directorio_actual)
main_path = os.path.dirname(path_web_app)
path_db = os.path.join(path_web_app, 'db.sqlite3')

#--------------------------------------------------------
conn = sqlite3.connect(path_db)
#--------------------------------------------------------------------------------------------------------------------
cursor = conn.cursor()
cursor.execute('SELECT Interfaz FROM home_configuraciones_generales')  # Reemplaza 'tu_tabla' con el nombre de tu tabla
registros = cursor.fetchall()
# Cierra la conexión con la base de datos
conn.close()

Interfaz = registros[0]
#---------------------------------------------------------

# Create your views here.

def obtener_ipv4_por_interfaz(interfaz):
    try:
        interfaces = psutil.net_if_addrs()
        
        for nombre, direcciones in interfaces.items():
            if nombre == interfaz:
                for direccion in direcciones:
                    if direccion.family == socket.AF_INET:
                        return direccion.address
        
        return None
    except Exception as e:
        print(f"Error al obtener la IP de la interfaz {interfaz}: {str(e)}")
        return None

# ip_server_ = obtener_ipv4_por_interfaz('Ethernet')        
ip_server_ = obtener_ipv4_por_interfaz(Interfaz[0])

print('-------------------------------------------------------------------------------')
print(f'server addr(grafana telegraf): {ip_server_}')
print('------------------------------------------------------------------------------')
#-----------------------------------------------------------------

@login_required
def index(request):
  context = {
    'ip_server': ip_server_
  }
  return render(request, 'pages/index.html', context)
        
def start_system(request):
    if request.method == 'GET':
        try:
            # Reemplaza 'nombre_del_programa' con el nombre o la ruta del programa que deseas ejecutar
            programa = os.path.join(main_path, 'start-system.bat')

            # Ejecuta el programa o script
            subprocess.Popen(['start', 'cmd', '/c', programa], shell=True)

            return HttpResponse(f'Se ejecutó exitosamente el programa: {programa}')
        except Exception as e:
            return HttpResponse(f'Error al ejecutar el programa: {str(e)}')

    return HttpResponse('Página de ejecución de programa. Use el formulario para ejecutar el programa.')

def stop_system(request):
    if request.method == 'GET':
        try:
            # Reemplaza 'nombre_del_programa' con el nombre o la ruta del programa que deseas ejecutar
            programa = os.path.join(main_path, 'task-kill.py')

            # Ejecuta el programa o script
            subprocess.Popen(['start', 'cmd', '/c', programa], shell=True)

            return HttpResponse(f'Se ejecutó exitosamente el programa: {programa}')
        except Exception as e:
            return HttpResponse(f'Error al ejecutar el programa: {str(e)}')

    return HttpResponse('Página de ejecución de programa. Use el formulario para ejecutar el programa.')
