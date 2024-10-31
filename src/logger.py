# src/logger.py
import logging
import os
from logging.handlers import RotatingFileHandler

# Configurações
LOG_CONFIG = {
    'DEFAULT_LEVEL': 'INFO',
    'LOG_DIRECTORY': '/home/igormedeiros/igor-repos/codeflow/logs',
    'LOG_FILENAME': 'app.log',
    'MAX_BYTES': 5 * 1024 * 1024,  # 5MB
    'BACKUP_COUNT': 5,
    'FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
}

def setup_logger():
    # Criar diretório de logs se não existir
    if not os.path.exists(LOG_CONFIG['LOG_DIRECTORY']):
        os.makedirs(LOG_CONFIG['LOG_DIRECTORY'])

    
    # Obter o nome da pasta raiz
    root_directory = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # Configuração do logger
    logger = logging.getLogger(root_directory)
    
    # Definir nível de log baseado na configuração ou variável de ambiente
    log_level = os.getenv('LOG_LEVEL', LOG_CONFIG['DEFAULT_LEVEL'])
    logger.setLevel(getattr(logging, log_level.upper()))

    # Evitar duplicação de handlers
    if not logger.handlers:
        # Formatter
        formatter = logging.Formatter(LOG_CONFIG['FORMAT'])

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(getattr(logging, log_level.upper()))

        # File handler
        file_handler = RotatingFileHandler(
            os.path.join(LOG_CONFIG['LOG_DIRECTORY'], LOG_CONFIG['LOG_FILENAME']),
            maxBytes=LOG_CONFIG['MAX_BYTES'],
            backupCount=LOG_CONFIG['BACKUP_COUNT']
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, log_level.upper()))

        # Adicionar handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger

# Criar instância única do logger
log = setup_logger()