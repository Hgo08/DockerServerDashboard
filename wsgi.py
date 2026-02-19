import sys
import os
from dotenv import load_dotenv

# 1. Añadir la ruta de la app al path de Python
sys.path.insert(0, '.')
load_dotenv('.env')

# load_dotenv('/var/www/tu_app/.env')

# activate_this = '/var/www/tu_app/venv/bin/activate_this.py'
# if os.path.exists(activate_this):
#     with open(activate_this) as f:
#         exec(f.read(), dict(__file__=activate_this))

from app import app as application
#script name/class name/application
