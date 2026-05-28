import os
import threading
import time
import psutil

class DatosGlobales:
    def __init__(self):
        self.processList = []
        self._lock = threading.Lock()
    
    def actualizar(self):
        with self._lock:
            self.processList = getAllProcess()

    def obtener_datos(self):
        """Obtiene una copia segura de los datos actuales"""
        with self._lock:
            return list(self.processList)

# Instancia global
datos_process = DatosGlobales()

def iniciar_actualizacion():
    """Inicia el hilo de actualización de datos"""
    def actualizar_datos():
        while True:
            datos_process.actualizar()
            time.sleep(1)
    
    hilo = threading.Thread(target=actualizar_datos, daemon=True)
    hilo.start()
    return hilo

def getAllProcess():

    #inicializamos la lista
    process = []

    #iteramos por los procesos obteniendo solo los datos que usamos
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):

        #intenta meter el proceso a la lista, si da un error de acceso denegado o el proceso no existe, salta al siguiente proceso
        try:
            process.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return process