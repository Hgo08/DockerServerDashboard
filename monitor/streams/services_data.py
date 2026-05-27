from flask import Blueprint, render_template
import psutil

# Creamos el blueprint para la pestaña de servicios
servicios_bp = Blueprint('servicios', __name__)

def obtener_procesos_activos():
    lista_procesos = []
    # Usamos psutil para espiar todos los procesos que corren en la máquina
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'status']):
        try:
            info = proc.info
            if not info['name']:
                info['name'] = "Proceso Desconocido"
            lista_procesos.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Si un proceso se cierra justo cuando lo miramos, pasamos al siguiente sin romper nada
            continue

    # Ordenamos los procesos de mayor a menor consumo de CPU
    lista_procesos.sort(key=lambda p: p['cpu_percent'], reverse=True)
    
    # Devolvemos solo los 10 primeros para no saturar la pantalla
    return lista_procesos[:10]


@servicios_bp.route('/servicios')
def servicios():
    # 1. Llamamos a la función para tener la lista con los 10 procesos reales
    mis_procesos = obtener_procesos_activos()
    
    # 2. Se los enviamos al HTML metidos dentro de la variable "procesos"
    return render_template('servicios.html', procesos=mis_procesos)