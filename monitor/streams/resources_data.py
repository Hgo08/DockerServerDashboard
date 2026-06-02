import threading
import time
import psutil

speed = 1

class DatosGlobales:
    def __init__(self):
        self.timestamp = time.strftime('%H:%M:%S')
        self.cpuTemp = 0
        self.cpu = 0

        self.usedRam = 0
        self.totalRam = 0

        self.netSent = psutil.net_io_counters().bytes_sent
        self.netRecv = psutil.net_io_counters().bytes_recv
        self.netSpeedSent = 0
        self.netSpeedRecv = 0

        self.diskRead = psutil.disk_io_counters().read_bytes
        self.diskWrite = psutil.disk_io_counters().write_bytes
        self.diskSpeedRead = 0
        self.diskSpeedWrite = 0

        self.diskSpaceUsed = 0
        self.diskSpaceTotal = 0

        self._lock = threading.Lock()
    
    def actualizar(self):
        """Actualiza los datos del sistema"""
        with self._lock:
            self.timestamp = time.strftime('%H:%M:%S')
            self.cpuTemp = psutil.sensors_temperatures()['coretemp'][0].current
            self.totalRam = psutil.virtual_memory().total
            self.usedRam = psutil.virtual_memory().used
            self.cpu = psutil.cpu_percent()

            self.netSpeedSent = (psutil.net_io_counters().bytes_sent - self.netSent)/speed
            self.netSpeedRecv = (psutil.net_io_counters().bytes_recv - self.netRecv)/speed

            self.netSent = psutil.net_io_counters().bytes_sent
            self.netRecv = psutil.net_io_counters().bytes_recv

            self.diskSpeedRead = (psutil.disk_io_counters().read_bytes - self.diskRead)/speed
            self.diskSpeedWrite = (psutil.disk_io_counters().write_bytes - self.diskWrite)/speed

            self.diskRead = psutil.disk_io_counters().read_bytes
            self.diskWrite = psutil.disk_io_counters().write_bytes

            self.diskSpaceUsed = psutil.disk_usage('/').used
            self.diskSpaceTotal = psutil.disk_usage('/').total
    
    def obtener_datos(self):
        """Obtiene una copia segura de los datos actuales"""
        with self._lock:
            return {
                'cpuTemp' : self.cpuTemp,
                'totalRam': bytes2GigaBytes(self.totalRam),
                'usedRam': bytes2GigaBytes(self.usedRam),
                'cpu': self.cpu,
                'timestamp': self.timestamp,

                'netSent': bytes2MegaBytes(self.netSent),
                'netRecv': bytes2MegaBytes(self.netRecv),
                'netSpeedRecv': bytes2MegaBytes(self.netSpeedRecv),
                'netSpeedSent': bytes2MegaBytes(self.netSpeedSent),

                'diskRead': bytes2MegaBytes(self.diskRead),
                'diskWrite': bytes2MegaBytes(self.diskWrite),
                'diskSpeedRead': bytes2MegaBytes(self.diskSpeedRead),
                'diskSpeedWrite': bytes2MegaBytes(self.diskSpeedWrite),

                'diskSpaceTotal': bytes2GigaBytes(self.diskSpaceTotal),
                'diskSpaceUsed': bytes2GigaBytes(self.diskSpaceUsed),
            }

# Instancia global
datos_recursos = DatosGlobales()

def iniciar_actualizacion():
    """Inicia el hilo de actualización de datos"""
    def actualizar_datos():
        while True:
            datos_recursos.actualizar()
            time.sleep(1)
    
    hilo = threading.Thread(target=actualizar_datos, daemon=True)
    hilo.start()
    return hilo

#funcion para pasar de bytes a gigabytes, solo divide entre 1024^3 (1073741824) y redondea a 2 decimales
def bytes2GigaBytes(bytes):
    return round(bytes/1073741824, 2)

#funcion para pasar de bytes a megabytes, solo divide entre 1024^2 (1048576) y redondea a 2 decimales
def bytes2MegaBytes(bytes):
    return round(bytes/1048576, 2)
