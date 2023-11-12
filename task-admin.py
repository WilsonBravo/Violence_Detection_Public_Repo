import psutil

procesos=["val-ips", "scraping.py", "ejecutarScriptExtraccionEKIA"]

value=input('Para verificar los procesos, ingrese "1" en caso contrario ingrese "0"\n')
if value == "1":

    # Puertos en los que se ejecutan tus proyectos Django
    puerto_Jobserver = [8000]
    puerto_Gestion = [8080]

    flag = False

    # Buscar procesos en los puertos del proyecto 1
    for conn in psutil.net_connections(kind='inet'):
        if conn.laddr.port in puerto_Jobserver:
            proceso = psutil.Process(conn.pid)
            print(f"El aplicativo de Jobservers (PID {proceso.pid}) está en ejecución en el puerto {conn.laddr.port}")

            flag = True

    if flag == False:
        print('El aplicativo de Jobservers no está en ejecución')

    flag = False

    # Buscar procesos en los puertos del proyecto 2
    for conn in psutil.net_connections(kind='inet'):
        if conn.laddr.port in puerto_Gestion:
            proceso = psutil.Process(conn.pid)
            print(f"El aplicativo de Gestion de contraseñas (PID {proceso.pid}) está en ejecución en el puerto {conn.laddr.port}")

            flag = True
    if flag == False:
        print('El aplicativo de Gestion de contraseñas no está en ejecución')

    for nombre_proceso in procesos:
        encontrado = False
        
        for proceso in psutil.process_iter(attrs=['pid', 'cmdline']):
            cmdline = proceso.info['cmdline']
            if cmdline and nombre_proceso in " ".join(cmdline):
                proceso_id = proceso.info['pid']
                encontrado = True
                print(f"Proceso {nombre_proceso} (PID {proceso_id}) está en ejecución.")
        
        if not encontrado:
            print(f"Proceso {nombre_proceso} no está en ejecución.")
else:
    pass

print('-------------------------------------------------------------------------')
print('procesos:')
print('-------------------------------------------------------------------------')
print('Ingrese "jobservers" para detener el aplicativo web de JobServers')
print('-------------------------------------------------------------------------')
print('Ingrese "gestion_psw" para detener el aplicativo web de Gestión de contraseñas')
print('-------------------------------------------------------------------------')
print('Ingrese "val-ips" para detener el aplicativo Python para la verificación de IPs de los dominios de JTeller')
print('-------------------------------------------------------------------------')
print('Ingrese "scraping.py" para detener el aplicativo de Monitoreo OIC')
print('-------------------------------------------------------------------------')
print('Ingrese "ejecutarScriptExtraccionEKIA" para detener el aplicativo de Extracción de Usuarios de Ekia')
# print('-------------------------------------------------------------------------')

procesos=[]

while True:
    print('-------------------------------------------------------------------------')
    value = input('ingrese el nombre de los procesos que desea detener,\n cuando termine de ingresar los nombres por favor ingrese la palabra "finalizar"\n')
    print('-------------------------------------------------------------------------')
    
    if value == "finalizar":
        break
    else:
        procesos.append(value)

for nombre_proceso in procesos:

    if nombre_proceso == "jobservers" or nombre_proceso == "gestion_psw":

        if nombre_proceso == "jobservers":
            puerto = [8000]
        elif nombre_proceso == "gestion_psw":
            puerto = [8080]

        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr.port in puerto:
                proceso_obj = psutil.Process(conn.pid)
                proceso_obj.terminate()  # Intenta cerrar el proceso
                print(f"Proceso {nombre_proceso} (PID {proceso_obj.pid}) ha sido terminado.")

    else:
        # Buscar procesos que coincidan con el comando
        for proceso in psutil.process_iter(attrs=['pid', 'cmdline']):
            cmdline = proceso.info['cmdline']
            if cmdline and nombre_proceso in " ".join(cmdline):
                proceso_id = proceso.info['pid']
                proceso_obj = psutil.Process(proceso_id)
                proceso_obj.terminate()  # Intenta cerrar el proceso
                print(f"Proceso {nombre_proceso} (PID {proceso_id}) ha sido terminado.")

input('ingrese cualquier tecla para terminar el programa\n')
