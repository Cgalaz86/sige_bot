"""
Sistema de logging centralizado
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from config.settings import LOGS_DIR

class Logger:
    """Clase para manejar logging tanto en archivo como en GUI"""
    
    def __init__(self, name: str = "SIGE_Bot", gui_callback: Optional[Callable[[str], None]] = None):
        self.gui_callback = gui_callback
        self.setup_file_logger(name)
    
    def setup_file_logger(self, name: str):
        """Configurar logging a archivo"""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Crear handler para archivo
        log_file = LOGS_DIR / f"sige_bot_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Formato de log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Evitar duplicar handlers
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
    
    def log(self, message: str, level: str = "INFO"):
        """
        Registrar mensaje en log y GUI
        
        Args:
            message: Mensaje a registrar
            level: Nivel del log (INFO, WARNING, ERROR)
        """
        # Log a archivo
        if level.upper() == "ERROR":
            self.logger.error(message)
        elif level.upper() == "WARNING":
            self.logger.warning(message)
        else:
            self.logger.info(message)
        
        # Log a GUI si existe callback
        if self.gui_callback:
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"
            self.gui_callback(formatted_message)
    
    def error(self, message: str):
        """Registrar mensaje de error"""
        self.log(f"❌ {message}", "ERROR")
    
    def warning(self, message: str):
        """Registrar mensaje de advertencia"""
        self.log(f"⚠ {message}", "WARNING")
    
    def info(self, message: str):
        """Registrar mensaje de información"""
        self.log(message, "INFO")
    
    def success(self, message: str):
        """Registrar mensaje de éxito"""
        self.log(f"✅ {message}", "INFO")
    
    def set_gui_callback(self, callback: Callable[[str], None]):
        """Establecer callback para logging en GUI"""
        self.gui_callback = callback