import logging
import sys
import inspect
import os
from typing import Optional
from functools import wraps


def get_caller_info():
    """Obtém informações do chamador para logging."""
    stack = inspect.stack()
    logger_module = __name__  # Nome do módulo atual (assumindo que este código está em core/logger.py)

    for frame_info in stack[2:]:  # Pular os dois primeiros frames (get_caller_info e _log)
        module = inspect.getmodule(frame_info.frame)
        if module and module.__name__ != logger_module:
            module_name = module.__name__
            filename = os.path.basename(module.__file__) if hasattr(module, '__file__') else "unknown"
            function_name = frame_info.function
            line_number = frame_info.lineno
            return (module_name, filename, function_name, line_number)

    # Se não encontrar nenhum chamador fora do logger, retornar desconhecido
    return ("unknown", "unknown", "unknown", 0)


class Logger:
    def __init__(self, name: str = "core", level: int = logging.INFO):
        """Inicializa o logger com configuração padrão."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Garante que o diretório de logs exista
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)

        if not self.logger.handlers:
            # Define o formato do log
            log_format = '%(asctime)s - %(name)s - %(levelname)s - [%(caller_file)s:%(caller_func)s:%(caller_lineno)d] - %(message)s'
            date_format = '%Y-%m-%d %H:%M:%S'

            # Handler para logs de informação
            info_handler = logging.FileHandler(f"{log_dir}/info.log")
            info_handler.setLevel(logging.DEBUG)
            info_handler.addFilter(lambda record: record.levelno <= logging.INFO)
            info_formatter = logging.Formatter(log_format, datefmt=date_format)
            info_handler.setFormatter(info_formatter)

            # Handler para logs de erro
            error_handler = logging.FileHandler(f"{log_dir}/error.log")
            error_handler.setLevel(logging.WARNING)
            error_formatter = logging.Formatter(log_format, datefmt=date_format)
            error_handler.setFormatter(error_formatter)

            # Handler para logs no console
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(log_format, datefmt=date_format)
            console_handler.setFormatter(console_formatter)

            # Adiciona os handlers ao logger
            self.logger.addHandler(info_handler)
            self.logger.addHandler(error_handler)
            self.logger.addHandler(console_handler)

    def _log(self, level: int, message: str, *args, **kwargs):
        """Método interno para logging com informações do chamador."""
        caller_module, file_name, func_name, line_no = get_caller_info()

        extra = kwargs.get('extra', {})
        extra.update({
            'caller_file': file_name,
            'caller_func': func_name,
            'caller_lineno': line_no  # Renomeado para evitar conflito
        })
        kwargs['extra'] = extra

        self.logger.log(level, message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        """Loga uma mensagem de nível INFO."""
        self._log(logging.INFO, message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """Loga uma mensagem de nível WARNING."""
        self._log(logging.WARNING, message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """Loga uma mensagem de nível ERROR."""
        self._log(logging.ERROR, message, *args, **kwargs)

    def debug(self, message: str, *args, **kwargs) -> None:
        """Loga uma mensagem de nível DEBUG."""
        self._log(logging.DEBUG, message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """Loga uma mensagem de nível CRITICAL."""
        self._log(logging.CRITICAL, message, *args, **kwargs)


# Instância global do logger
log = Logger()
