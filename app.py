from flask import Flask, render_template, Response, redirect, url_for, session, request
from functools import wraps
import psutil
import time
import json
import threading
import os

app = Flask(__name__, template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY')

USUARIO = os.environ.get('USUARIO_ADMIN')
PASSWORD = os.environ.get('PASSWORD_ADMIN')

# Verificar que las variables existen
if not app.secret_key or not USUARIO or not PASSWORD:
    raise RuntimeError("Error al cargar las varibles de entorno .env, comprueba el path si existen las variables")

# ── Decorador para proteger rutas ─────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ── Auth ──────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['usuario'] == USUARIO and request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('monitor'))
        else:
            error = 'Credenciales incorrectas'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ── Rutas ──────────────────────────────────────────
@app.route('/')
@app.route('/monitor')
@login_required
def monitor():
    return render_template('monitor.html')

@app.route('/logs')
@login_required
def logs():
    return render_template('logs.html')

@app.route('/services')
@login_required
def services():
    return render_template('services.html')

@app.route('/pages')
@login_required
def pages():
    return render_template('pages.html')

@app.route('/users')
@login_required
def users():
    return render_template('users.html')

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

# ── Stream ──────────────────────────────────────────

@app.route('/monitor-stream')
@login_required
def stream():
    def generar_eventos():
        while True:
            with datos._lock:
                datos_actuales = {
                    'contador': datos.contador,
                    'timestamp': datos.timestamp,
                    'cpu': datos.cpu
                }
            yield f"data: {json.dumps(datos_actuales)}\n\n"
            time.sleep(1)

    response = Response(generar_eventos(), mimetype='text/event-stream')
    response.headers['X-Accel-Buffering'] = 'no'
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    return response

# ── Datos y hilo (igual que antes) ───────────────────────────
class DatosGlobales:
    def __init__(self):
        self.contador = 0
        self.timestamp = time.strftime('%H:%M:%S')
        self.cpu = 0

        self._lock = threading.Lock()

datos = DatosGlobales()

def actualizar_datos():
    while True:
        with datos._lock:
            datos.contador += 1
            datos.timestamp = time.strftime('%H:%M:%S')
            datos.cpu = psutil.cpu_percent()

        time.sleep(1)

hilo_actualizacion = threading.Thread(target=actualizar_datos, daemon=True)
hilo_actualizacion.start()

if __name__ == '__main__':
    app.run(debug=False)