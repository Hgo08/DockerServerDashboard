import os
import sys
from dotenv import load_dotenv

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    load_dotenv(os.path.join(BASE_DIR, '.env'))

    SECRET_KEY = os.environ.get('SECRET_KEY')
    USUARIO_ADMIN = os.environ.get('USUARIO_ADMIN')
    PASSWORD_ADMIN = os.environ.get('PASSWORD_ADMIN')
    
    @staticmethod
    def validate():
        """Valida que todas las variables requeridas estén configuradas"""
        if not Config.SECRET_KEY or not Config.USUARIO_ADMIN or not Config.PASSWORD_ADMIN:
            raise RuntimeError(
                "Error al cargar las variables de entorno .env, "
                "comprueba el path si existen las variables"
            )