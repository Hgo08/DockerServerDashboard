import psutil

def obtener_procesos_activos():
    lista_procesos = []
    
    # Recorremos todos los procesos que hay en el servidor
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'status']):
        try:
            # Sacamos la información de cada uno
            info = proc.info
            # Si el proceso no tiene nombre, le ponemos un valor por defecto
            if not info['name']:
                info['name'] = "Proceso Desconocido"
                
            lista_procesos.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Si un proceso se cierra justo cuando lo miramos, pasamos al siguiente
            continue

    # Los ordenamos de mayor a menor consumo de CPU
    lista_procesos.sort(key=lambda p: p['cpu_percent'], reverse=True)
    
    # Devolvemos solo los 10 primeros para que la lista quede limpia
    return lista_procesos[:10]