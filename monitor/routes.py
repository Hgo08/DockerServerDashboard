from flask import Blueprint, render_template, Response
import json
import time
from decorators import login_required
from .streams.resources_data import datos_recursos

monitor_bp = Blueprint('monitor', __name__)

@monitor_bp.route('/')
@monitor_bp.route('/monitor')
@login_required
def monitor():
    return render_template('monitor.html')

@monitor_bp.route('/process')
@login_required
def process():
    return render_template('process.html')

@monitor_bp.route('/logs')
@login_required
def logs():
    return render_template('logs.html')

@monitor_bp.route('/disks')
@login_required
def disks():
    return render_template('disks.html')

@monitor_bp.route('/services')
@login_required
def services():
    return render_template('services.html')

@monitor_bp.route('/pages')
@login_required
def pages():
    return render_template('pages.html')

@monitor_bp.route('/users')
@login_required
def users():
    return render_template('users.html')

@monitor_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@monitor_bp.route('/settings/update', methods=['POST'])
def update_settings():
    # Iteramos sobre todo lo que venga en el form
    for key, value in request.form.items():
        setting = Setting.query.get(key)
        if setting:
            setting.value = value
        else:
            db.session.add(Setting(key=key, value=value))
    
    # Lógica especial para el switch (checkbox)
    # Si no llega en el form es que está "off"
    if 'ocultar_procesos' not in request.form:
        s = Setting.query.get('ocultar_procesos')
        if s: s.value = 'false'
    
    db.session.commit()
    return redirect(url_for('monitor.settings_page'))