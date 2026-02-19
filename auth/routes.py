from flask import Blueprint, render_template, redirect, url_for, session, request
from config import Config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        
        if usuario == Config.USUARIO_ADMIN and password == Config.PASSWORD_ADMIN:
            session['logged_in'] = True
            return redirect(url_for('monitor.monitor'))
        else:
            error = 'Credenciales incorrectas'
    
    return render_template('login.html', error=error)

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))