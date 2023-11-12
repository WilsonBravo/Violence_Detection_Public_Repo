import cv2
import numpy as np
import asyncio
import websockets
import socket
import threading
from queue import Queue
import os
import pymysql
import sys

import tensorflow as tf
import gc

# Registra una consulta en la tabla de registro
def registrar_consulta(cur, conn, consulta, exitosa=True):
    query = "INSERT INTO registro_consultas (consulta, exitosa) VALUES (%s, %s);"
    cur.execute(query, (consulta, exitosa))
    conn.commit()

def conectar_base_de_datos():

    conn = pymysql.connect(
        host=host,
        user=usuario,
        password=contraseña,
        database=base_de_datos
    )
    
    return conn


# > ### Funcion de registro de valores

# In[9]:

try:
    # importar variables del archivo .py
    #-------------------------------------------------------
    from variables import cap_type, max_frames, shared_folder,server_ip
    from variables import host, usuario, contraseña, base_de_datos
    #-------------------------------------------------------


    # path
    #-------------------------------------------------------------
    # directorio_actual = os.path.dirname(os.path.abspath(__file__))
    # shared_folder = os.path.join(directorio_actual, 'frames')


    # Obtener IP
    #-------------------------------------------------------
    # def obtener_ipv4():
    #     hostname = socket.gethostname()
    #     direcciones_ipv4 = socket.gethostbyname_ex(hostname)
    #     ipv4 = direcciones_ipv4[2][0]
    #     return ipv4
    # ipv4 = obtener_ipv4()
    # print('tu dirección IP es:',ipv4)

    # Variables cámara
    #-----------------------------------------------------------------------------------
    print(cap_type)
    #cap_type = 0
    # cap_type = 'http://192.168.3.101:4747/video'
    option = 1
    # message = True
    # max_frames = 80

    #--------control de escritura------------------------
    # Configuración del servidor para recibir comandos de control
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, 8888))
    server_socket.listen(1)

    # Código para escribir datos en el archivo
    client_socket, _ = server_socket.accept()
    client_socket.settimeout(5/100)

    #--------------------------------------------------------
    img_size = 224
    img_size_touple = (img_size, img_size)

    # Variables globales para compartir datos entre hilos
    # frame_queue = Queue()
    break_flag_queu = Queue()
    frame_save_queue = Queue()
    websocket_clients = set()

    # Nueva función para guardar los fotogramas en disco
    def frames_list():
        global option
        global images
        global frame_count

        while True:
            # Recibir mensaje de socket para control de escritura
            # print('recibiendo mensaje..')
            try:
                mensaje = client_socket.recv(1024)
                # print(f'se recibió el siguiente mensaje: {mensaje.decode()}')

                if mensaje.decode() == '\x01':
                    images = []
                    frame_count = 0
                    option = 0
            # print('\x01')
            except Exception as e:
                # print('no se recibió mensaje')
                # mensaje = None
                pass

    # Nueva función para guardar los fotogramas en disco
    def save_frames_to_disk():
        # global client_socket
        while True:
            frames = frame_save_queue.get()
            if frames is None:
                break

            frames = np.array(frames)
            frames = (frames / 255.).astype(np.float16)

            print('inicia guardado')
            for num_frame in range(max_frames):

                file_name = f'frames_{num_frame}.npy'
                file_path = os.path.join(shared_folder, file_name)

                np.save(file_path, frames[num_frame])
                
            print('termina guardado')
            client_socket.send(b'\x01')

            gc.collect()
            tf.compat.v1.reset_default_graph()            

    # Función para capturar frames y guardar datos
    def capture_frames():
        global option
        global images
        global frame_count
        global frame_g

        # global client_socket
        while True:
            ret, frame = cap.read()

            if not ret:
                break

            # cv2.imshow('Camera', frame)
            # cv2.waitKey(1)

            frame_g = frame

            # Guarda el frame en la cola para su posterior transmisión
            # frame_queue.put(frame)

            if option == 0 and frame_count<max_frames:
                RGB_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                res = cv2.resize(RGB_frame, dsize=img_size_touple, interpolation=cv2.INTER_CUBIC)
                images.append(res)

                frame_count += 1

            elif option == 0 and frame_count>=max_frames:
                frame_save_queue.put(images)
                option = 1

    async def handle_websockets(websocket, path):
        # Agregar el cliente WebSocket al conjunto de clientes
        global frame_g
        websocket_clients.add(websocket)
        try:
            while True:
                # Obtener un frame de la cola y enviarlo a través del WebSocket
                # frame = frame_queue.get()
                _, jpeg = cv2.imencode('.jpg', frame_g)
                await websocket.send(jpeg.tobytes())
        except websockets.exceptions.ConnectionClosedError:
            pass
        finally:
            # Eliminar el cliente WebSocket del conjunto de clientes
                websocket_clients.remove(websocket)
except Exception as e:
    print("Error:", e)
    # Llamar a la función para conectar a la base de datos
    conn = conectar_base_de_datos()
    # Crear un cursor
    cur = conn.cursor()
    registrar_consulta(cur, conn, e, exitosa=False)  # Registra la consulta con error  
    # Cerrar la conexión
    cur.close()
    conn.close()
    # Terminar el programa
    sys.exit()  

if __name__ == "__main__":

    try:
        # fps = 30 #*
        cap = cv2.VideoCapture(cap_type)
        # cap.set(cv2.CAP_PROP_FPS, fps) # Establece la tasa de FPS #*

        server_thread = threading.Thread(target=capture_frames)
        # Hilo para crear la lista de frames
        frames_list_thread = threading.Thread(target=frames_list)
        # Creamos un nuevo hilo para guardar en disco
        save_thread = threading.Thread(target=save_frames_to_disk)


        server_thread.start()
        frames_list_thread.start()
        save_thread.start()

        asyncio.get_event_loop().run_until_complete(
            websockets.serve(handle_websockets, server_ip, 8765)
        )
        asyncio.get_event_loop().run_forever()

    except Exception as e:

        print("Error:", e)
        # Llamar a la función para conectar a la base de datos
        conn = conectar_base_de_datos()
        # Crear un cursor
        cur = conn.cursor()
        registrar_consulta(cur, conn, e, exitosa=False)  # Registra la consulta con error  
        # Cerrar la conexión
        cur.close()
        conn.close()