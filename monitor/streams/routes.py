from flask import Blueprint, Response, request, render_template, current_app
import json
import time
from decorators import login_required
from .resources_data import datos_recursos
from .logs_data import datos_logs
from .process_data import datos_process 
from .disks_data import datos_disks

# Crear blueprint para streams
streams_bp = Blueprint('streams', __name__)

@streams_bp.route('/monitor-stream')
@login_required
def monitor_stream():
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


@streams_bp.route('/process-stream')
@login_required
def process_stream():
    #obtenemos los parametros de la URL, si no existen se usa por defecto el segundo valor ('' y 'cpu_percent)
    search = request.args.get('search', '').lower()
    sort_by = request.args.get('sort', 'cpu_percent')
    inverted = request.args.get('inverted', 'false').lower() == 'true'

    app = current_app._get_current_object()

    def generar_eventos():
        with app.app_context():
            while True:
                #obtenemos todos los procesos desde el hilo de actualizacion
                allProcess = datos_process.obtener_datos()

                #inicializamos la lista
                filtred = []

                #solo filtrar si la busqueda no esta vacia
                #if search != '':
                for proc in allProcess:
                    #por cada proceso, se obtiene su nombre y su PID
                    #(se usa 'or' para establecer un valor por defecto por si no se puede acceder a 'name' o 'pid' y asi evitar errores)
                    nombre = str(proc.get('name') or '').lower()
                    pid = str(proc.get('pid') or '')
                    #si la busqueda contiene el nombre o el pid del proceso de la iteracion actual, se añade a la lista de procesos filtrados
                    if search in nombre or search in pid:
                        filtred.append(proc)

                #ordena los procesos filtrados, usando una funcion lambda para ordenarlos por la variable sort_by y que no de error si no tiene valor
                ordered = sorted(filtred, key=lambda x: x.get(sort_by) if x.get(sort_by) is not None else 0, reverse=inverted)

                #genera el html de los procesos desde un template pasando como variable la lista de todos los porcesos (limitado a 30)
                html = render_template('partials/process.html', procesos=ordered[:30])
                html_limpio = html.replace('\n', '').replace('\r', '')


                yield f"data: {html_limpio}\n\n"
                time.sleep(1)

    return Response(generar_eventos(), mimetype='text/event-stream')


@streams_bp.route('/disks-stream')
@login_required
def disks_stream():
    app = current_app._get_current_object()

    def generar_eventos():
        with app.app_context():
            while True:

                #obtenemos todos los discos desde el hilo de actualizacion
                disksData = datos_disks.obtener_datos()

                #genera el html de los discos desde un template pasando como variable la lista de todos los discos
                html = render_template('partials/disk_parts.html', disks=disksData['partitions'])
                disk_parts_clean = html.replace('\n', '').replace('\r', '')

                html = render_template('partials/disk_devices.html', disks=disksData['devices'])
                disk_devices_clean = html.replace('\n', '').replace('\r', '')

                data = {
                    "disk_parts_html": disk_parts_clean,
                    "disk_devices_html": disk_devices_clean
                }

                yield f"data: {json.dumps(data)}\n\n"
                time.sleep(1)

    return Response(generar_eventos(), mimetype='text/event-stream')