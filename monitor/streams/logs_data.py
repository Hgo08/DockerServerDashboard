import os
import threading
import time

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
                f.seek(self.ultima_posicion)       # Solo lee desde donde quedó
                nuevas = f.readlines()
                self.ultima_posicion = f.tell()    # Guarda la posición actual

            if nuevas:
                for linea in nuevas:
                    linea_limpia = linea.strip()
                    if linea_limpia != "":
                        self.lineas.append(linea_limpia)

    def obtener_datos(self):
        """Obtiene una copia segura de los datos actuales"""
        with self._lock:
            return {
                'logs': "\n".join(self.lineas)
            }

# Instancia global
# datos_logs = DatosGlobales("C:/Users/Victor/Desktop/log.txt")
datos_logs = DatosGlobales("/var/log/apache2/access.log")

def iniciar_actualizacion():
    """Inicia el hilo de actualización de datos"""
    def actualizar_datos():
        while True:
            datos_logs.actualizar()
            time.sleep(1)
    
    hilo = threading.Thread(target=actualizar_datos, daemon=True)
    hilo.start()
    return hilo