from flask import Flask
from config import Config
from auth import auth_bp
from monitor import monitor_bp, streams_bp, iniciar_logs, iniciar_resources


def create_app():
    app = Flask(__name__, template_folder='templates')
    
    # Configuración
    app.config.from_object(Config)
    app.secret_key = Config.SECRET_KEY
    Config.validate()
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(monitor_bp)
    app.register_blueprint(streams_bp)
    
    # Iniciar actualización de datos
    iniciar_logs()
    iniciar_resources()
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=False)