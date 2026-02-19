from flask import Blueprint, Response
import json
import time
from decorators import login_required
from .data_manager import datos

# Crear blueprint para streams
streams_bp = Blueprint('streams', __name__)

@streams_bp.route('/monitor-stream')
@login_required
def stream():
    def generar_eventos():
        while True:
            datos_actuales = datos.obtener_datos()
            yield f"data: {json.dumps(datos_actuales)}\n\n"
            time.sleep(1)

    response = Response(generar_eventos(), mimetype='text/event-stream')
    response.headers['X-Accel-Buffering'] = 'no'
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    return response