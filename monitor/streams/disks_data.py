import os
import threading
import time
import psutil
from pySMART import Device, DeviceList

class DatosGlobales:
    def __init__(self):
        self.partitions = []
        self.devices = []
        self._lock = threading.Lock()

        self.last_io = {} 
        self.last_time = time.time()
    
    def actualizar(self):
        current_io = psutil.disk_io_counters(perdisk=True)
        current_time = time.time()
        time_delta = current_time - self.last_time

        partitionsWithoutSpace = psutil.disk_partitions()
        completePartitions = []

        for part in partitionsWithoutSpace:
            try:
                uso = psutil.disk_usage(part.mountpoint)

                datos_particion = {
                "device": part.device,
                "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "opts": part.opts,
                "total": bytes2GB(uso.total),
                "used": bytes2GB(uso.used),
                "free": bytes2GB(uso.free),
                "percent": uso.percent
                }
                completePartitions.append(datos_particion)
            except PermissionError:
                # Esto sucede a veces con unidades de CD-ROM o discos externos protegidos
                print(f"Permiso denegado para acceder a {p.mountpoint}")
                continue
            except OSError:
                # Sucede si un disco se desconectó justo en el proceso
                continue

        current_devices = []
        try:
            devicelist = DeviceList()
            for device in devicelist:
                # El nombre en pySMART es '/dev/sda', pero en psutil es 'sda'
                disk_name_short = os.path.basename(device.name)

                io_key = None
                
                # 1. Intento directo (SATA/USB: 'sda' == 'sda')
                if disk_name_short in current_io:
                    io_key = disk_name_short
                else:
                    # 2. Intento difuso (NVMe/SD: 'nvme0' -> busca algo que empiece por 'nvme0')
                    # Filtramos para evitar particiones (buscamos el nombre más corto que coincida)
                    matches = [k for k in current_io.keys() if k.startswith(disk_name_short)]
                    if matches:
                        # Ordenamos por longitud para pillar 'nvme0n1' antes que 'nvme0n1p1'
                        io_key = sorted(matches, key=len)[0]

                read_speed = 0.0
                write_speed = 0.0

                # Calcular velocidades si encontramos la llave y tenemos historial
                if io_key and io_key in self.last_io:
                    old = self.last_io[io_key]
                    curr = current_io[io_key]
                    
                    read_speed = (curr.read_bytes - old.read_bytes) / time_delta / (1024 * 1024)
                    write_speed = (curr.write_bytes - old.write_bytes) / time_delta / (1024 * 1024)
            
                current_devices.append({
                    "name": device.name,           # Ej: /dev/sda
                    "model": device.model,         # Ej: ST10000DM0004
                    "temp": device.temperature,    # Ej: 34 (en grados C)
                    "health": device.assessment,   # Ej: PASS 
                    "read_speed": f"{round(read_speed, 2)} MB/s",
                    "write_speed": f"{round(write_speed, 2)} MB/s"
                })
        except Exception as e:
            print(f"Error al leer SMART: {e}")

        # Guardar estado para la próxima iteración
        self.last_io = current_io
        self.last_time = current_time

        with self._lock:
            self.partitions = completePartitions
            self.devices = current_devices

    def obtener_datos(self):
        """Obtiene una copia segura de los datos actuales"""
        with self._lock:
            return {
                'partitions': self.partitions,
                'devices': self.devices
            }

# Instancia global
datos_disks = DatosGlobales()

def iniciar_actualizacion():
    """Inicia el hilo de actualización de datos"""
    def actualizar_datos():
        while True:
            datos_disks.actualizar()
            time.sleep(1)
    
    hilo = threading.Thread(target=actualizar_datos, daemon=True)
    hilo.start()
    return hilo


def bytes2GB(bytes):
    return round(bytes / 1073741824, 2)