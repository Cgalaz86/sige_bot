"""
Configuraciones generales del proyecto SIGE Bot
"""
import os
from pathlib import Path

# Rutas del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DOWNLOADS_DIR = DATA_DIR / "downloads"
LOGS_DIR = DOWNLOADS_DIR / "logs"

# URLs del sistema SIGE
SIGE_LOGIN_URL = "https://sige.mineduc.cl/Sige/Login"

# Configuraciones de Selenium
SELENIUM_TIMEOUT = 15
MAX_LOGIN_ATTEMPTS = 10
CHROME_DRIVER_PATH = "/opt/homebrew/bin/chromedriver"  # Ajustar según tu sistema

# Archivos de datos
CONNECTIONS_FILE = DATA_DIR / "conexiones.txt"

# Perfiles disponibles en SIGE
AVAILABLE_PROFILES = {
    "1": "Establecimiento Subv.",
    "2": "Sostenedor",
    "3": "Establecimiento Particular y DL 3166",
    "4": "Sala Cuna-Jardin"
}

# Años disponibles para exportación
AVAILABLE_YEARS = list(range(2020, 2026))
DEFAULT_YEAR = "2025"

# Crear directorios necesarios
def create_directories():
    """Crear directorios necesarios para el proyecto"""
    directories = [
        DATA_DIR,
        DOWNLOADS_DIR,
        DOWNLOADS_DIR / "matricula",
        DOWNLOADS_DIR / "datos_colegio",
        LOGS_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Crear directorios al importar el módulo
create_directories()