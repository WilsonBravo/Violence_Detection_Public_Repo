import psutil

procesos=["start-system", "cod_modelo_035_frames", "start-camara", "camara_loop"]

for proceso in procesos:
    # Nombre del proceso que deseas buscar (sin la extensión .bat)
    nombre_proceso = proceso

    # Buscar procesos que coincidan con el comando
    for proceso in psutil.process_iter(attrs=['pid', 'cmdline']):
        cmdline = proceso.info['cmdline']
        if cmdline and nombre_proceso in " ".join(cmdline):
            proceso_id = proceso.info['pid']
            proceso_obj = psutil.Process(proceso_id)
            proceso_obj.terminate()  # Intenta cerrar el proceso
            print(f"Proceso {nombre_proceso} (PID {proceso_id}) ha sido terminado.")

