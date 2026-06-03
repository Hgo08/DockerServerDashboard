import os
import threading
import time
import psutil
from pySMART import Device, DeviceList
from db_models import Setting


class DatosGlobales:
    def __init__(self):
        self.partitions = []
        self.devices = []
        self._lock = threading.Lock()

        self.last_io = {} 
        self.last_time = time.time()
    
    def actualizar(self, app):
        with app.app_context():
            update_delay = Setting.get_val('update_interval', 1)
            tempUnit = Setting.get_val('temp_unit', 'C')
            diskUnit = Setting.get_val('disk_units', '')

        current_io = psutil.disk_io_counters(perdisk=True)
        current_time = time.time()
        time_delta = current_time - self.last_time

        partitionsWithoutSpace = psutil.disk_partitions()
        completePartitions = []
        fs_ignorar = {'tmpfs', 'devtmpfs', 'devfs', 'overlay', 'shm', 'squashfs'}

        for part in partitionsWithoutSpace:
            # FILTROS CRÍTICOS:
            # 1. Debe tener un nombre de dispositivo real (/dev/...)
            if not part.device.startswith('/dev/'):
                continue
            # 2. Ignorar sistemas de archivos virtuales/Docker
            if part.fstype in fs_ignorar:
                continue
            # 3. Ignorar montajes específicos de archivos de Docker
            if any(x in part.mountpoint for x in ['/etc/hosts', '/etc/hostname', '/etc/resolv.conf', '/docker']):
                continue
            try:
                space = psutil.disk_usage(part.mountpoint)

                display_mount = part.mountpoint.replace('/host', '')
                if display_mount == "": display_mount = "/"

                bytesTotal = space.total
                bytesUsed = space.used
                bytesFree = space.free

                if (diskUnit == 'GB'):
                    spaceTotal = bytes2GB(bytesTotal)
                    spaceUsed  = bytes2GB(bytesUsed)
                    spaceFree  = bytes2GB(bytesFree)
                else:
                    spaceTotal = bytes2GiB(bytesTotal)
                    spaceUsed  = bytes2GiB(bytesUsed)
                    spaceFree  = bytes2GiB(bytesFree)

                datos_particion = {
                    "device": part.device,
                    "mountpoint": display_mount,
                    "fstype": part.fstype,
                    "opts": part.opts,
                    "total": spaceTotal,
                    "used": spaceUsed,
                    "free": spaceFree,
                    "percent": space.percent
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
                
                celsius = device.temperature

                if tempUnit == 'F':
                    temp = str(round(celsius * 1.8 + 32)) + "º" + tempUnit
                else:
                    temp = str(celsius) + "º" + tempUnit
                
                diskSize = 'N/A'

                if (device.capacity):
                    diskSizeBytes = parse_capacity(device.capacity)
                    if (diskUnit == 'GB'):
                        diskSize = bytes2GB(diskSizeBytes)
                    else:
                        diskSize = bytes2GiB(diskSizeBytes)
                else:
                    diskSize = 'N/A'
            
                current_devices.append({
                    "name": device.name,           # Ej: /dev/sda
                    "model": device.model,         # Ej: ST10000DM0004
                    "temp": temp,    # Ej: 34ºC
                    "health": device.assessment,   # Ej: PASS 
                    "read_speed": f"{round(read_speed, 2)} MB/s",
                    "write_speed": f"{round(write_speed, 2)} MB/s",
                    "size": f"{diskSize}{diskUnit}"
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

def iniciar_actualizacion(app):
    """Inicia el hilo de actualización de datos"""
    def actualizar_datos():
        while True:
            with app.app_context():
                update_delay = float(Setting.get_val('update_interval', 1))
                
            datos_disks.actualizar(app)
            time.sleep(update_delay)
    
    hilo = threading.Thread(target=actualizar_datos, daemon=True)
    hilo.start()
    return hilo



def _obtener_tamano_fisico(disk_name):
        """Lee el tamaño total del disco desde /sys/block en GB"""
        try:
            disk_name = os.path.basename(disk_name)
            # En Linux, 'size' contiene el número de sectores de 512 bytes
            with open(f"/sys/block/{disk_name}n1/size", "r") as f:
                sectores = int(f.read().strip())
                return bytes2GB(sectores * 512)
        except Exception as e:
            return e

def parse_capacity(capacity_str):
    value, unit = capacity_str.split()
    value = float(value)

    unit = unit.upper()

    if unit == "TB":
        return value * 1000**4
    elif unit == "GB":
        return value * 1000**3
    elif unit == "MB":
        return value * 1000**2
    elif unit == "KB":
        return value * 1000
    else:
        return value  # bytes o desconocido

def bytes2GiB(bytes_):
    return round(bytes_ / 1073741824, 2)

def bytes2GB(bytes_):
    return round(bytes_ / 1_000_000_000, 2)