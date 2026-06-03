from flask import Blueprint, render_template, Response, request, redirect, url_for
import json
import time
from decorators import login_required
from .streams.resources_data import datos_recursos
from db_models import db, Setting

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
@login_required # Si tienes este decorador, úsalo aquí también
def update_settings():
    # 1. Guardar lo que llega (Selects y Checkboxes marcados)
    for key, value in request.form.items():
        setting = Setting.query.get(key)
        if setting:
            setting.value = value
        else:
            db.session.add(Setting(key=key, value=value))
    
    # 2. Caso especial: Checkboxes no marcados
    # Si 'hide_sys_procs' no está en request.form, es que el usuario lo apagó
    if 'hide_sys_procs' not in request.form:
        s = Setting.query.get('hide_sys_procs')
        if s:
            s.value = 'false'
        else:
            db.session.add(Setting(key='hide_sys_procs', value='false'))
    
    db.session.commit()
    
    # Redirigir de vuelta a la página de ajustes
    return redirect(url_for('monitor.settings'))