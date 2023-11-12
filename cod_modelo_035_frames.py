# Librerías para manipulación de imágenes y datos
# import cv2
import datetime
import sys
import numpy as np
import imageio
import os
import pickle

import threading
from queue import Queue

# Librerías de machine learning y deep learning
import tensorflow
import gc
from tensorflow.keras.models import Model
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import load_model

# Librerías para manipulación de archivos y tiempo
from IPython.display import clear_output

# Librerías para manejo de datos SQL y sockets
import socket
import pymysql

# Librerías para Bot de Telegram
import asyncio
from telegram import Bot
from telegram import InputFile

# In[8]:


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


def insertar_prediccion(valor_prediccion, cur, conn):
    
    #consulta para registrar ubicación de donde se emitieron los valores
    consulta_ubicación = "INSERT INTO ubicaciones (latitud, longitud) VALUES (%s, %s);"

    # consulta para registrar valores de predicción de violencia
    consulta_prediccion = 'INSERT INTO predicciones (valor_prediccion) VALUES (%s)'
    valor_prediccion = valor_prediccion  # Cambia esto al valor que deseas insertar

    try:
        cur.execute(consulta_prediccion, (valor_prediccion,))
        # registrar_consulta(cur, conn, consulta_prediccion, exitosa=True)  # Registra la consulta exitosa
        cur.execute(consulta_ubicación, (latitude, longitude))
        # registrar_consulta(cur, conn, consulta_ubicación, exitosa=True)  # Registra la consulta exitosa
    except Exception as e:
        print("Error:", e)
        registrar_consulta(cur, conn, e, exitosa=False)  # Registra la consulta con error
        # registrar_consulta(cur, conn, consulta_ubicación, exitosa=False)  # Registra la consulta con error

    conn.commit()

# > Inicializar modelo y directorio de videos de prueba

# In[3]:
try:
    # importar variables del archivo .py
    from variables import host, usuario, contraseña, base_de_datos, server_ip
    from variables import shared_folder, video_path, model_path, output_path
    from variables import latitude, longitude, fps_cam, max_frames, freq_send_message
    from variables import group_id, chat_id, mensaje_id, acces_token_alert, acces_token_db

    # server_ip = 'localhost'

    #-----------------------------------------------------------------------------------
    #------------------------------------------------------------------------------------
    model = load_model(model_path)

    send_message_queue = Queue()

    # ## Variables

    # In[4]:

    #----------------------------------------------------------------------------
    # Frame size  
    img_size = 224
    img_size_touple = (img_size, img_size)

    # Number of channels (RGB)
    num_channels = 3

    # Flat frame size
    img_size_flat = img_size * img_size * num_channels

    # Number of classes for classification (Violence-No Violence)
    num_classes = 2

    # Number of frames per video
    _images_per_file = 20

    # variable de control de envío de mensajes
    bot_message_flag = 0
    hora_inicio = datetime.datetime.now()
    hora_final = datetime.datetime.now()

    #---------------------------------------------------------------------------------------
    #---------------------------------------------------------------------------------------

    # Configuración del cliente para recibir señales de escritura
    # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # client_socket.connect((server_ip, 8888))

    # client_socket.send(b'\x01')

    # ## Modelo MobileNetV2

    # In[5]:


    # Cargar el modelo MobileNetV2 preentrenado sin incluir las capas completamente conectadas (top)
    image_model = MobileNetV2(weights='imagenet', include_top=True, alpha=0.35)

    # Seleccionar la última capa convolucional como capa de transferencia de características
    transfer_layer = image_model.layers[-2]  # Cambiar a -1 si es la última capa

    # Crear un nuevo modelo que toma la entrada del MobileNetV2 y produce las salidas de la capa seleccionada
    image_model_transfer = Model(inputs=image_model.input,
                                outputs=transfer_layer.output)

    transfer_values_size = transfer_layer.output_shape[-1]

    print("The input of the MobileNetV2 network has dimensions:", image_model.input_shape[1:3])
    print("The output of the selected layer of MobileNetV2 has dimensions:", transfer_values_size)

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

# ## Funciones

# > ### Función para procesar los cuadros de video a través del modelo Pre-Entrenado y obtener valores de transferencia.

# In[6]:


def get_transfer_values():
    
    # Preasignar una matriz de lotes de entrada para las imágenes.
    shape = (_images_per_file,) + img_size_touple + (3,)
    
    image_batch = np.zeros(shape=shape, dtype=np.float16)
    
    # print('inicia lectura de los datos')
    
    # Define el número total de frames que quieres cargar
    num_frames = max_frames

    # Crea una lista para almacenar los frames cargados
    frames_list = []
    
    # Carga cada frame y agrega a la lista
    for num_frame in range(num_frames):
        
        file_name = f'frames_{num_frame}.npy'
        file_path = os.path.join(shared_folder, file_name)
                
        frame = np.load(file_path)
        frames_list.append(frame)
        
    # client_socket.send(b'\x01')
    # DATO LEIDO
    with open("myfile.pickle", "wb") as outfile: 
        pickle.dump(1, outfile)

    #--------------------------------------------------------------------
    image_batch = np.array(frames_list)
    frames = (image_batch*255).astype('uint8')
    #-------------------------------------------------------------------------
    
    # print('termina lectura de los datos')
    
    # Preasignar una matriz de salida para los valores de transferencia.
    # Ten en cuenta que se usan puntos flotantes de 16 bits para ahorrar memoria.
    
    shape = (_images_per_file, transfer_values_size)
    transfer_values = np.zeros(shape=shape, dtype=np.float16)
    # print('inicia procesamiento a traves del modelo MobileNetV2')

    transfer_values = image_model_transfer.predict(image_batch)
            
    return transfer_values, frames


# In[7]:


def process_data_eval(data):
    
    joint_transfer=[]
    frames_num=20
    count = 0

    for i in range(int(len(data)/frames_num)):
        inc = count+frames_num
        joint_transfer.append([data[count:inc]])
        count =inc
        
    data =[]
    
    for i in joint_transfer:
        data.append(i[0])
        
    return data


# ### Funciones SQL

# > ### Función para registrar log de consultas y conectar a la base de datos


# ### Función de predicción

# > ### Función para enviar el mensaje de alerta

# In[10]:


def prediction_alert(predictions, predict_threshold, output_folder, frames):
    alert = 0
    
    # Variables    
    idx_predict = 0

    # Configuración del video
    seg_num = 0
    idx_video_num = 0

    fps = fps_cam  # Fotogramas por segundo del video
    height, width, _ = frames[0].shape  # Dimensiones de los frames
    
    # base_filename = 'temp_video'  # Nombre base del archivo de video
    base_filename = f'temp_video_{idx_video_num}.mp4'
    # output_path = f'{output_folder}{base_filename}_{idx_video_num}.mp4'  # Ruta donde deseas guardar el video
    output_path = os.path.join(output_folder, base_filename)

    # Crear un objeto VideoWriter
    writer = imageio.get_writer(output_path, format='FFMPEG',mode='I',fps=fps_cam)

    for elements in predictions:

        if predictions[idx_predict] > predict_threshold:
            
            # Alertar
            alert = 1

            print("Predicción:", predictions[idx_predict])

            for i in range(idx_predict*20, (idx_predict*20)+20):

                writer.append_data(frames[i])

            seg_num += 1

            if seg_num > 5:

                seg_num = 0
                # out.release()
                writer.close()

                idx_video_num += 1

                base_filename = f'temp_video_{idx_video_num}.mp4'
                # output_path = f'{output_folder}{base_filename}_{idx_video_num}.mp4'  # Ruta donde deseas guardar el video
                output_path = os.path.join(output_folder, base_filename)

                # Crear un objeto VideoWriter
                writer = imageio.get_writer(output_path, format='FFMPEG',mode='I',fps = fps_cam)
                
        idx_predict += 1

    # Liberar el objeto VideoWriter
    writer.close()
    return alert

async def send_alert(prediction):
    #variables
    global bot_message_flag
    global hora_final
    global hora_inicio

    predict_treshold = 0.1

    if prediction > predict_treshold and bot_message_flag == 0:

        message_text = f"¡Alerta! Se detectó una posible situación de violencia (prediction: {prediction})"
        chat_id_send = group_id
        # Bot de Telegram
        bot = Bot(token = acces_token_alert)
        #---------------------------------------------------------------------------------------------------------------
        #---------------------------------------------------------------------------------------------------------------
        bot_message_flag = 1

        # Enviar la ubicación al chat
        await bot.send_message(chat_id=chat_id_send, text=message_text, reply_to_message_id=mensaje_id)

        # Enviar el video al chat
        with open(video_path, 'rb') as video_file:
            video = InputFile(video_file)
            await bot.send_video(chat_id=chat_id_send, video=video, reply_to_message_id=mensaje_id)

        # Enviar la ubicación al chat
        await bot.send_location(chat_id=chat_id_send, latitude=latitude, longitude=longitude, reply_to_message_id=mensaje_id)
        # Guardar la hora de inicio
        hora_inicio = datetime.datetime.now()

    elif prediction > predict_treshold and bot_message_flag == 1:

        message_text = f"(prediction: {prediction})"
        chat_id_send = chat_id
        # Bot de Telegram
        bot = Bot(token = acces_token_alert)

        # Imprimir la hora de inicio y finalización
        # print("Hora de inicio:", hora_inicio.strftime("%Y-%m-%d %H:%M:%S"))
        # print("Hora de finalización:", hora_final.strftime("%Y-%m-%d %H:%M:%S"))

        # Enviar la ubicación al chat
        await bot.send_message(chat_id=chat_id_send, text=message_text)

        # Enviar el video al chat
        with open(video_path, 'rb') as video_file:
            video = InputFile(video_file)
            await bot.send_video(chat_id=chat_id_send, video=video)

        # Enviar la ubicación al chat
        await bot.send_location(chat_id=chat_id_send, latitude=latitude, longitude=longitude)

        if hora_inicio is not None:
        
            # Guardar la hora de finalización
            hora_final = datetime.datetime.now()
            # Calcular la diferencia en segundos
            
            diferencia = (hora_final - hora_inicio).total_seconds()
            # print (diferencia)

            if diferencia > freq_send_message:
                bot_message_flag = 0

    elif prediction < predict_treshold:

        message_text = f"(prediction: {prediction})"
        chat_id_send = chat_id
        # Bot de Telegram
        bot = Bot(token = acces_token_db)

        # Imprimir la hora de inicio y finalización
        # print("Hora de inicio:", hora_inicio.strftime("%Y-%m-%d %H:%M:%S"))
        # print("Hora de finalización:", hora_final.strftime("%Y-%m-%d %H:%M:%S"))
        # Enviar la ubicación al chat
        await bot.send_message(chat_id=chat_id_send, text=message_text)

        # Enviar el video al chat
        with open(video_path, 'rb') as video_file:
            video = InputFile(video_file)
            await bot.send_video(chat_id=chat_id_send, video=video)

        # Enviar la ubicación al chat
        await bot.send_location(chat_id=chat_id_send, latitude=latitude, longitude=longitude)
    
        if hora_inicio is not None:
            # Guardar la hora de finalización
            hora_final = datetime.datetime.now()

            # Calcular la diferencia en segundos
            diferencia = (hora_final - hora_inicio).total_seconds()
            # print (diferencia)

            if diferencia > freq_send_message:
                bot_message_flag = 0

    # Enviar la ubicación al chat
    # await bot.send_message(chat_id=chat_id_send, text=message_text, reply_to_message_id=mensaje_id)

    # Enviar el video al chat
    # with open(video_path, 'rb') as video_file:
    #     video = InputFile(video_file)
    #     await bot.send_video(chat_id=chat_id_send, video=video, reply_to_message_id=mensaje_id)

    # Enviar la ubicación al chat
    # await bot.send_location(chat_id=chat_id_send, latitude=latitude, longitude=longitude, reply_to_message_id=mensaje_id)

# # Realizar predicción
async def send_message_telegram():
    while True:
        print('**********************************************************')
        predictions = send_message_queue.get()
        # print(frames)
        if predictions is not None:

            try:    
                # hora_start_test = datetime.datetime.now()

                await send_alert(np.mean(predictions))

                # hora_end_test = datetime.datetime.now()

                # Calcular la diferencia en segundos
                # diferencia = (hora_end_test - hora_start_test).total_seconds()
                # print (f'Enviar Alerta Telegram: {diferencia}')
                    
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

            # ENVIAR DATOS A LA BASE DE DATOS SQL
            #--------------------------------------------------------------------------------------------
            try:
                # hora_start_test = datetime.datetime.now()
                # Llamar a la función para conectar a la base de datos
                conn = conectar_base_de_datos()
                # Crear un cursor
                cur = conn.cursor()

                insertar_prediccion(np.mean(predictions), cur, conn)

                # Cerrar la conexión
                cur.close()
                conn.close()
                # hora_end_test = datetime.datetime.now()

                # Calcular la diferencia en segundos
                # diferencia = (hora_end_test - hora_start_test).total_seconds()
                # print (f'Guardar datos base de datos: {diferencia}')
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

# In[15]:
async def main():
    #---------------------------------------------------------------
    # hora_start_test = datetime.datetime.now()

    stop_loop = False
    
    while not stop_loop:
        try:  
            # CONTROL LECTURA      
            # mensaje = client_socket.recv(1024)

            try:
                with open("myfile.pickle", "rb") as infile: 
                    mensaje = pickle.load(infile) 
            except Exception as e:
                mensaje = 0 # Escribiendo
                
            # if mensaje.decode() == '\x01':
            if mensaje == 2:
                # print('----------------------------------------------------------------------------------')
                # hora_end_test = datetime.datetime.now()

                # Calcular la diferencia en segundos
                # diferencia = (hora_end_test - hora_start_test).total_seconds()
                # print (f'Guardar Frames desde la cámara: {diferencia}')

                # hora_start_test = datetime.datetime.now()

                # predicción: [[Violencia | No_Violencia]]
                # Preprocesar los frames del video
                predict_threshold = 0
                
                # print('se inicia el procesamiento mobilenetv2')
            
                # Datos a predecir
                data_eval, frames = get_transfer_values()
                
                #-------------Lectura del archivo compartido terminada--------------

                # print('termina procesamiento')
                
                #-------------------------------------------------------------------
                
                data_eval = process_data_eval(data_eval)

                # hora_end_test = datetime.datetime.now()

                # Calcular la diferencia en segundos
                # diferencia = (hora_end_test - hora_start_test).total_seconds()
                # print (f'Lectura: {diferencia}')

                # hora_start_test = datetime.datetime.now()
            
                output_folder = output_path  # Carpeta donde deseas guardar los videos
            
                # Realizar la predicción
                # print('inicia predicción')
                predictions = model.predict(np.array(data_eval))

                # hora_end_test = datetime.datetime.now()

                # Calcular la diferencia en segundos
                # diferencia = (hora_end_test - hora_start_test).total_seconds()
                # print (f'Procesamiento: {diferencia}')

                predictions = predictions[:,0]
                # print('termina predicción')

                # hora_start_test = datetime.datetime.now()

                telegram_alert = prediction_alert(predictions, predict_threshold, output_folder, frames)
                send_message_queue.put(predictions)

                # hora_end_test = datetime.datetime.now()

                # Calcular la diferencia en segundos
                # diferencia = (hora_end_test - hora_start_test).total_seconds()
                # print (f'Guardar video: {diferencia}')

                # DATO LEIDO
                # with open("myfile.pickle", "wb") as outfile: 
                #     pickle.dump(1, outfile)
            
                # MENSAJE DE TELEGRAM
                #--------------------------------------------------------------------------------------------------
                '''
                
                try:    
                    hora_start_test = datetime.datetime.now()

                    await send_alert(np.mean(predictions))

                    hora_end_test = datetime.datetime.now()

                    # Calcular la diferencia en segundos
                    diferencia = (hora_end_test - hora_start_test).total_seconds()
                    print (f'Enviar Alerta Telegram: {diferencia}')
                        
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

                # ENVIAR DATOS A LA BASE DE DATOS SQL
                #--------------------------------------------------------------------------------------------
                try:
                    hora_start_test = datetime.datetime.now()
                    # Llamar a la función para conectar a la base de datos
                    conn = conectar_base_de_datos()
                    # Crear un cursor
                    cur = conn.cursor()
                
                    insertar_prediccion(np.mean(predictions), cur, conn)
                
                    # Cerrar la conexión
                    cur.close()
                    conn.close()
                    hora_end_test = datetime.datetime.now()

                    # Calcular la diferencia en segundos
                    diferencia = (hora_end_test - hora_start_test).total_seconds()
                    print (f'Guardar datos base de datos: {diferencia}')
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
                '''
                
                clear_output()

                # DATO LEIDO
                # with open("myfile.pickle", "wb") as outfile: 
                #     pickle.dump(1, outfile)

                # hora_start_test = datetime.datetime.now()

                gc.collect()
                tensorflow.compat.v1.reset_default_graph()
                # print('----------------------------------------------------------------------------------')

        except socket.error as e:

            print("Error:", e)
            # Llamar a la función para conectar a la base de datos
            conn = conectar_base_de_datos()
            # Crear un cursor
            cur = conn.cursor()
            registrar_consulta(cur, conn, e, exitosa=False)  # Registra la consulta con error  
            # Cerrar la conexión
            cur.close()
            conn.close() 
            sys.exit()   

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
    #--------------------------------------------------------------------------------------------

# Run the event loop
if __name__ == "__main__":

    # telegram_thread = threading.Thread(target=send_message_telegram)
    # telegram_thread.start()

    telegram_thread = threading.Thread(target=lambda: asyncio.run(send_message_telegram()))
    telegram_thread.start()
    
    asyncio.run(main())
