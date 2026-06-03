from flask import Flask
from config import Config
from auth import auth_bp
from db_models import db, Setting
from monitor import monitor_bp, streams_bp, iniciar_logs, iniciar_resources, iniciar_process, iniciar_disks


def create_app():
    app = Flask(__name__, template_folder='templates')
    
    # Configuración de SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    @app.context_processor
    def inject_settings():
        # Consultamos la base de datos y creamos un diccionario
        # Si la tabla está vacía, devolverá un diccionario vacío {}
        try:
            all_settings = {s.key: s.value for s in Setting.query.all()}
        except:
            all_settings = {}
        return dict(settings=all_settings)

    with app.app_context():
        db.create_all()

    # Configuración de flask
    app.config.from_object(Config)
    app.secret_key = Config.SECRET_KEY
    Config.validate()
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(monitor_bp)
    app.register_blueprint(streams_bp)
    
    # Iniciar actualización de datos
    iniciar_logs()
    iniciar_resources(app)
    iniciar_process(app)
    iniciar_disks(app)
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)