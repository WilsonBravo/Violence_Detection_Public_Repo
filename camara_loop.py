import cv2
import numpy as np
import socket
import os

#-------------------------------------------------------
from variables import cap_type, max_frames, shared_folder
#-------------------------------------------------------
def obtener_ipv4():
    hostname = socket.gethostname()
    direcciones_ipv4 = socket.gethostbyname_ex(hostname)
    ipv4 = direcciones_ipv4[2][0]
    return ipv4

ipv4 = obtener_ipv4()

print('tu dirección IP es:',ipv4)
#--------control de escritura------------------------
# Configuración del servidor para recibir comandos de control
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((ipv4, 8888))
server_socket.listen(1)

# Código para escribir datos en el archivo
client_socket, _ = server_socket.accept()

#--------------------------------------------------------
img_size = 224
img_size_touple = (img_size, img_size)

# Funcion capturar frames
def capture_frames():

        images = []
        frame_count = 0

        while frame_count < max_frames:
                            
            ret, frame = cap.read()
            
            if not ret:
                break
            
            RGB_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            res = cv2.resize(RGB_frame, dsize=img_size_touple, interpolation=cv2.INTER_CUBIC)
            images.append(res)
            
            cv2.imshow('Camera', frame)
            cv2.waitKey(1)

            frame_count += 1
        
        frames = np.array(images)
        frames = (frames / 255.).astype(np.float16)
        capture_camera()

        return frames


# Funcion guardar datos
def save_data(frames):

    print('inicia guardado')
    for num_frame in range(max_frames):
        
        capture_camera()
        file_name = f'frames_{num_frame}.npy'
        file_path = os.path.join(shared_folder, file_name)
        
        capture_camera()
        np.save(file_path, frames[num_frame])
        
    print('termina guardado')
    client_socket.send(b'\x01')
    capture_camera()


# Funcion capturar camara
def capture_camera():
    ret, frame = cap.read()
    cv2.imshow('Camera', frame)
    cv2.waitKey(1)

#--------------------------------------------------------------

stop_loop = False

fps = 30
cap = cv2.VideoCapture(cap_type)
cap.set(cv2.CAP_PROP_FPS, fps) # Establece la tasa de FPS 

while not stop_loop:
    break_flag = False
# -----------------------------------------------------------------  
    mensaje = client_socket.recv(1024)
    
    if mensaje.decode() == '\x01':
        while not break_flag:
            try:
                frames = capture_frames()
                save_data(frames)
                break_flag = True
            except Exception as e:
                # break_flag = False
                print(e)
                print("\n Por favor revisar el estado de su red, si el problema persiste reinicie el programa.")
                cap.release()
                cv2.destroyAllWindows()
                cap = cv2.VideoCapture(cap_type)
                cap.set(cv2.CAP_PROP_FPS, fps) # Establece la tasa de FPS 
                 

    else:
        try:
            capture_camera()
        except Exception as e:
            print(e)
            print("\n Por favor revisar el estado de su red, si el problema persiste reinicie el programa.")
            cap.release()
            cv2.destroyAllWindows()
            cap = cv2.VideoCapture(cap_type)
            cap.set(cv2.CAP_PROP_FPS, fps) # Establece la tasa de FPS 
              