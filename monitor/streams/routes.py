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

