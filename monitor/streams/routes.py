from flask import Blueprint, Response, render_template
import json
import time
from decorators import login_required
from .resources_data import datos_recursos
from .logs_data import datos_logs

# Crear blueprint para streams
streams_bp = Blueprint('streams', __name__)

@streams_bp.route('/monitor-stream')
@login_required
def stream():
    def generar_eventos():
        while True:
            datos_actuales = datos_recursos.obtener_datos()
            yield f"data: {json.dumps(datos_actuales)}\n\n"
            time.sleep(1)

    response = Response(generar_eventos(), mimetype='text/event-stream')
    response.headers['X-Accel-Buffering'] = 'no'
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    return response


@streams_bp.route('/logs-stream')
@login_required
def logs_stream():
    def generar_eventos():
         while True:
            datos_actuales = datos_logs.obtener_datos()
            yield f"data: {json.dumps(datos_actuales)}\n\n"
            time.sleep(1)

    response = Response(generar_eventos(), mimetype='text/event-stream')
    response.headers['X-Accel-Buffering'] = 'no'
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'

    return response

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