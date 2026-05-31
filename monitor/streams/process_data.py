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
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_info']):
        #intenta meter el proceso a la lista, si da un error de acceso denegado o el proceso no existe, salta al siguiente proceso
        try:
            process.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'username': proc.info['username'],
                                'cpu_percent': proc.info['cpu_percent'],
                                'ram': bytes2MB(proc.info['memory_info'].rss)
                            })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return process

#convierte de bytes a una unidad legible
def bytes2Human(bytes):
    actual = bytes
    #mientras que la unidad acutal sea mayor a 1024, la pasamos a la siguiente unidad (bytes -> KB)
    while actual > 1024:
        actual = actual / 1024
    
    #cuando ya no sea mayor, devuelve
def bytes2MB(bytes):
    return round(bytes / 1048576, 2)