import logging
import os
from logging.handlers import RotatingFileHandler

from .singleton import SingletonMeta

# pylint: disable=bare-except, broad-exception-caught, invalid-name


class Logger(metaclass=SingletonMeta):
    def __init__(self, name) -> None:
        self.logger = None
        self.name = name

    def get_logger(self):
        if self.logger is None:
            self.logger = AbstractLogger().get_logger(self.name)
        return self.logger
    
    def read_log_file(self):
        log_file = os.path.join(AbstractLogger().log_dir, "measurekiller.log")
        try:
            with open(log_file, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            return f"Log file not found: {log_file}"
        except PermissionError:
            return f"Permission denied while reading log file: {log_file}"
        except Exception as e:
            return f"Error reading log file: {e}"

class AbstractLogger:
    def __init__(self) -> None:
        self.application_path = os.path.dirname(os.path.abspath(__file__))
        self.log_dir = os.path.join(os.environ['APPDATA'], 'Measure Killer', 'log')
        self.create_log_dir()

    def create_log_dir(self):
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def get_logger(self, name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        log_file = os.path.join(self.log_dir, "measurekiller.log")
        file_handler = RotatingFileHandler(log_file, maxBytes=5e6, backupCount=5, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)

        if not logger.hasHandlers():
            logger.addHandler(file_handler)

        return logger

    