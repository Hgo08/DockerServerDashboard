import os
import threading
import time

class DatosGlobales:
    def __init__(self, ruta_log):
        self.ruta_log = ruta_log
        self.ultima_posicion = 0
        self.lineas = []
        self._lock = threading.Lock()
    
    def actualizar(self, app):
        with app.app_context():
            update_delay = Setting.get_val('update_interval', 1)
        if not os.path.exists(self.ruta_log):
            return
        with self._lock:
            with open(self.ruta_log, "r") as f:
                self.lineas = [] 
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
datos_logs = DatosGlobales("")

def iniciar_actualizacion(app):
    """Inicia el hilo de actualización de datos"""
    def actualizar_datos():
        while True:
            with app.app_context():
                update_delay = float(Setting.get_val('update_interval', 1))
                
            datos_logs.actualizar(app)
            time.sleep(update_delay)
    
    hilo = threading.Thread(target=actualizar_datos, daemon=True)
    hilo.start()
    return hilo