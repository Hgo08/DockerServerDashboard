from .routes import streams_bp
from .resources_data import iniciar_actualizacion as iniciar_resources
from .process_data import iniciar_actualizacion as iniciar_process
from .logs_data import iniciar_actualizacion as iniciar_logs
from .disks_data import iniciar_actualizacion as iniciar_disks
__all__ = ['streams_bp']