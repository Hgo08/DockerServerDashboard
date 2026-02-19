from flask import Blueprint, render_template, Response
import json
import time
from decorators import login_required
from .streams.data_manager import datos

monitor_bp = Blueprint('monitor', __name__)

@monitor_bp.route('/')
@monitor_bp.route('/monitor')
@login_required
def monitor():
    return render_template('monitor.html')

@monitor_bp.route('/logs')
@login_required
def logs():
    return render_template('logs.html')

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