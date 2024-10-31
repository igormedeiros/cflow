# config.py
import os

# Configurações do logger
LOG_CONFIG = {
    'DEFAULT_LEVEL': 'INFO',  # Nível padrão de log
    'LOG_DIRECTORY': '/home/igormedeiros/igor-repos/codeflow/logs',
    'LOG_FILENAME': 'app.log',
    'MAX_BYTES': 5 * 1024 * 1024,  # 5MB
    'BACKUP_COUNT': 5,
    'FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
}