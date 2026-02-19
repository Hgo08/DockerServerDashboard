import threading
import time
import psutil

class DatosGlobales:
    def __init__(self):
        self.contador = 0
        self.timestamp = time.strftime('%H:%M:%S')
        self.cpu = 0
        self._lock = threading.Lock()
    
    def actualizar(self):
        """Actualiza los datos del sistema"""
        with self._lock:
            self.contador += 1
            self.timestamp = time.strftime('%H:%M:%S')
            self.cpu = psutil.cpu_percent()
    
    def obtener_datos(self):
        """Obtiene una copia segura de los datos actuales"""
        with self._lock:
            return {
                'contador': self.contador,
                'timestamp': self.timestamp,
                'cpu': self.cpu
            }

# Instancia global
datos = DatosGlobales()

def iniciar_actualizacion():
    """Inicia el hilo de actualización de datos"""
    def actualizar_datos():
        while True:
            datos.actualizar()
            time.sleep(1)
    
    hilo = threading.Thread(target=actualizar_datos, daemon=True)
    hilo.start()
    return hilo