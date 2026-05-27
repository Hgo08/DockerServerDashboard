import threading
import time
import psutil

class DatosGlobales:
    def __init__(self):
        self.contador = 0
        self.timestamp = time.strftime('%H:%M:%S')
        
        # --- CLAVES IDÉNTICAS A TU JAVASCRIPT ---
        self.temperatura = 0
        self.cpu = 0
        self.ram = 0
        self.red = 0
        
        # Guardamos los bytes antiguos para poder calcular los MB/s reales
        self.red_bytes_antiguos = psutil.net_io_counters().bytes_recv
        self.lock = threading.Lock()

    def actualizar(self):
        """Actualiza los datos de hardware (Ejecutado por el hilo secundario)"""
        with self.lock:
            self.contador += 1
            self.timestamp = time.strftime('%H:%M:%S')
            
            # 1. CPU: Saca el porcentaje de uso actual
            self.cpu = round(psutil.cpu_percent(), 1)
            
            # 2. RAM: Tu JS espera directamente los GB usados para calcularlo sobre el tope de 16
            memoria = psutil.virtual_memory()
            self.ram = round(memoria.used / (1024 ** 3), 2) # Convierte bytes a GB usados
            
            # 3. RED: Calculamos la velocidad de descarga en MB/s
            bytes_actuales = psutil.net_io_counters().bytes_recv
            bytes_dif = bytes_actuales - self.red_bytes_antiguos
            self.red_bytes_antiguos = bytes_actuales
            self.red = round(bytes_dif / (1024 * 1024), 2) # Convierte a Megabytes por segundo
            
            # 4. TEMPERATURA: Captura el sensor térmico principal en Linux
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    primera_clave = list(temps.keys())[0]
                    self.temperatura = round(temps[primera_clave][0].current, 1)
                else:
                    self.temperatura = 0
            except AttributeError:
                self.temperatura = 0 # Evita que pete si haces pruebas en local con Windows

    def obtener_datos(self):
        """Devuelve el diccionario exacto que tu JSON.parse va a devorar"""
        with self.lock:
            return {
                'contador': self.contador,
                'timestamp': self.timestamp,
                'temperatura': self.temperatura,
                'cpu': self.cpu,
                'ram': self.ram,
                'red': self.red
            }

# Instancia global que importa tu blueprint de rutas
datos_recursos = DatosGlobales()

def iniciar_actualizacion():
    """Lanza el hilo en segundo plano para actualizar los datos cada segundo"""
    def actualizar_datos():
        while True:
            datos_recursos.actualizar()
            time.sleep(1)
            
    hilo = threading.Thread(target=actualizar_datos, daemon=True)
    hilo.start()
    return hilo