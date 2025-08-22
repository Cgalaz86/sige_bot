"""
Archivo principal para ejecutar SIGE Bot
"""
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path para imports
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from gui.main_window import MainWindow
from config.settings import create_directories

def main():
    """Función principal"""
    try:
        # Asegurar que los directorios necesarios existen
        create_directories()
        
        # Crear y ejecutar la aplicación
        app = MainWindow()
        app.run()
        
    except KeyboardInterrupt:
        print("\nAplicación interrumpida por el usuario.")
    except Exception as e:
        print(f"Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()