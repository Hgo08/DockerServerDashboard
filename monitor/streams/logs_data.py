import os
import threading
import time

max_lineas = 1000

class DatosGlobales:
    def __init__(self, ruta_log):
        self.ruta_log = ruta_log
        self.ultima_posicion = 0
        self.lineas = []
        self._lock = threading.Lock()
    
    def actualizar(self):
        if not os.path.exists(self.ruta_log):
            print("la ruta no existe")
            return
        with self._lock:
            with open(self.ruta_log, "r") as f:
                f.seek(self.ultima_posicion)
                nuevas = f.readlines()
                self.ultima_posicion = f.tell()
            if nuevas:
                for linea in nuevas:
                    linea_limpia = linea.strip()
                    if linea_limpia != "":
                        self.lineas.append(linea_limpia)
                if len(self.lineas) > max_lineas:
                    self.lineas = self.lineas[-max_lineas:]

    def obtener_datos(self):
        """Obtiene una copia segura de los datos actuales"""
        with self._lock:
            return {
                'logs': "\n".join(self.lineas)
            }

# Instancia global
datos_logs = DatosGlobales("C:\\Users\\Adminlocal\\Desktop\\logs.txt")
def iniciar_actualizacion():
    """Inicia el hilo de actualización de datos"""
    def actualizar_datos():
        while True:
            datos_logs.actualizar()
            time.sleep(1)
    
    hilo = threading.Thread(target=actualizar_datos, daemon=True)
    hilo.start()
    return hilo