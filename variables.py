import socket
import sqlite3
import os
import psutil

# Frecuencia de envío de mensajes
freq_send_message = 30

# Obtén el directorio actual del archivo .py
# directorio_actual = os.path.dirname(os.path.abspath(__file__))
# Retrocede un nivel para llegar al directorio padre
# directorio_padre = os.path.dirname(directorio_actual)
# print("Directorio padre:", directorio_padre)

# Obtén el directorio actual del archivo .py
directorio_actual = os.path.dirname(os.path.abspath(__file__))
path_web_app = os.path.join(directorio_actual, 'web_app')
path_db = os.path.join(path_web_app, 'db.sqlite3')

# Establece la conexión con la base de datos SQLite (reemplaza 'nombre_de_tu_base_de_datos.db' con el nombre de tu base de datos)
conn = sqlite3.connect(path_db)
#--------------------------------------------------------------------------------------------------------------------
cursor = conn.cursor()

# Ejecutar una consulta SQL para seleccionar todos los registros de una tabla
cursor.execute('SELECT * FROM home_configuraciones_generales')  # Reemplaza 'tu_tabla' con el nombre de tu tabla

# Obtener todos los registros de la consulta
registros = cursor.fetchall()
data_conf_gen = registros[0]

#----------------- TELEGRAM----------------------------------
#------------------------------------------------------------
canal_id, group_id = data_conf_gen[11].split(',')
chat_id = data_conf_gen[1]
acces_token_alert = data_conf_gen[2]
acces_token_db = data_conf_gen[3]
mensaje_id = data_conf_gen[10]

#----------------- SQL --------------------------------------
#------------------------------------------------------------
# Valores de la base de datos
host = data_conf_gen[4]
usuario = data_conf_gen[5]
contraseña = data_conf_gen[6]
base_de_datos = data_conf_gen[7]
#----------------------------------------------------------------------
#----------------------------------------------------------------------
Interfaz = data_conf_gen[9]
#----------------------------------------------------------------------
#----------------------------------------------------------------------

# Ejecutar una consulta SQL para seleccionar todos los registros de una tabla
cursor.execute('SELECT * FROM home_configuraciones_del_sistema')  # Reemplaza 'tu_tabla' con el nombre de tu tabla

# Obtener todos los registros de la consulta
registros = cursor.fetchall()
data_conf_gen = registros[0]

# Obtener los nombres de las columnas de la tabla

#----------------geolocalizacion----------------------------------------
#-----------------------------------------------------------------------
latitude = float(data_conf_gen[1])
longitude = float(data_conf_gen[2])
#-----------------CAMARA---------------------------------------
#-------------------------------------------------------------
ip_camera_address=data_conf_gen[3]
camera_option = data_conf_gen[4]
local_camara = int(data_conf_gen[5])
max_frames = int(data_conf_gen[6])
fps_cam = int(data_conf_gen[8])

# Directorios
shared_folder = os.path.join(directorio_actual, 'frames') + os.sep
# --------------------------------------------------------------
video_path= os.path.join(directorio_actual, 'video')
video_path= os.path.join(video_path, 'temp_video_0.mp4')
#----------------------------------------------------------------
video_test_path= os.path.join(directorio_actual, 'video_test')
video_test_path= os.path.join(video_test_path, 'video_test.avi')
#----------------------------------------------------------------
model_path= os.path.join(directorio_actual, 'modelo')
model_path= os.path.join(model_path, 'MobileNetV2_LSTM.h5')
#----------------------------------------------------------------
output_path= os.path.join(directorio_actual, 'video') + os.sep
#-----------------------------------------------------------------------

# Camara Local
if camera_option == "0":
    cap_type = local_camara

# Camara IP
elif camera_option == "1":  
    # Solicitar al usuario que ingrese la dirección IP
    camera_port = 554  # Puerto para el protocolo RTSP
    # URL de la cámara IP con el protocolo RTSP
    rtsp_url = f'rtsp://{ip_camera_address}:{camera_port}/'
    # rtsp_url = f"rtsp://admin:@{ip_camera_address}/H264?ch=1&subtype=1"

    cap_type = rtsp_url

elif camera_option == "2":  

    cap_type = f'http://{ip_camera_address}:4747/video'

elif camera_option == "3":
    cap_type = video_test_path

# Cierra la conexión con la base de datos
conn.close()

# server_ip = input("ingrese la ip destino para el socket :")
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

server_ip = obtener_ipv4_por_interfaz(Interfaz)
print('--------------------------------------------------')
print(f'La dirección de la interfaz {Interfaz} es: {server_ip}')
print('--------------------------------------------------')