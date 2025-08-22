"""
Utilidades para manejo de archivos
"""
from pathlib import Path
import os
from datetime import datetime

def generate_unique_filename(directory: Path, base_name: str, extension: str) -> Path:
    """
    Generar un nombre de archivo único en el directorio especificado
    
    Args:
        directory: Directorio donde se guardará el archivo
        base_name: Nombre base del archivo (sin extensión)
        extension: Extensión del archivo (incluyendo el punto)
        
    Returns:
        Path completo del archivo único
    """
    directory = Path(directory)
    contador = 1
    
    while True:
        filename = f"{base_name}_{contador}{extension}"
        filepath = directory / filename
        
        if not filepath.exists():
            return filepath
        
        contador += 1

def ensure_directory_exists(directory: Path) -> None:
    """
    Asegurar que un directorio existe, creándolo si es necesario
    
    Args:
        directory: Directorio a verificar/crear
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

def get_file_size(filepath: Path) -> str:
    """
    Obtener el tamaño de un archivo en formato legible
    
    Args:
        filepath: Ruta del archivo
        
    Returns:
        Tamaño en formato legible (KB, MB, GB)
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        return "0 B"
    
    size_bytes = filepath.stat().st_size
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.1f} TB"

def get_timestamp_string(format_str: str = "%Y%m%d_%H%M%S") -> str:
    """
    Obtener timestamp actual en formato string
    
    Args:
        format_str: Formato del timestamp
        
    Returns:
        Timestamp formateado
    """
    return datetime.now().strftime(format_str)

def clean_filename(filename: str) -> str:
    """
    Limpiar nombre de archivo removiendo caracteres no válidos
    
    Args:
        filename: Nombre de archivo original
        
    Returns:
        Nombre de archivo limpio
    """
    # Caracteres no válidos en nombres de archivo
    invalid_chars = '<>:"/\\|?*'
    
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remover espacios múltiples y al inicio/final
    filename = ' '.join(filename.split())
    
    return filename

def list_files_in_directory(directory: Path, extension: str = None) -> list:
    """
    Listar archivos en un directorio
    
    Args:
        directory: Directorio a listar
        extension: Extensión específica a filtrar (opcional)
        
    Returns:
        Lista de archivos Path
    """
    directory = Path(directory)
    
    if not directory.exists():
        return []
    
    if extension:
        if not extension.startswith('.'):
            extension = f'.{extension}'
        return [f for f in directory.iterdir() if f.is_file() and f.suffix.lower() == extension.lower()]
    else:
        return [f for f in directory.iterdir() if f.is_file()]

def move_file_safely(source: Path, destination: Path) -> bool:
    """
    Mover archivo de forma segura, creando directorios si es necesario
    
    Args:
        source: Archivo origen
        destination: Archivo destino
        
    Returns:
        True si se movió exitosamente
    """
    try:
        source = Path(source)
        destination = Path(destination)
        
        # Crear directorio destino si no existe
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        # Si el archivo destino ya existe, generar nombre único
        if destination.exists():
            base_name = destination.stem
            extension = destination.suffix
            destination = generate_unique_filename(destination.parent, base_name, extension)
        
        # Mover archivo
        source.rename(destination)
        return True
        
    except Exception as e:
        print(f"Error moviendo archivo: {e}")
        return False