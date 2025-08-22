"""
Utilidades de validación
"""
import re
from typing import Optional

def validate_rbd(rbd: str) -> bool:
    """
    Validar formato de RBD (Rol Base de Datos)
    
    Args:
        rbd: String con el RBD a validar
        
    Returns:
        True si el formato es válido
    """
    if not rbd:
        return False
    
    # RBD debe ser numérico y tener entre 3 y 6 dígitos
    return rbd.isdigit() and 3 <= len(rbd) <= 6

def validate_rut(rut: str) -> bool:
    """
    Validar formato y dígito verificador de RUT chileno
    
    Args:
        rut: String con el RUT a validar (formato: 12345678-9)
        
    Returns:
        True si el RUT es válido
    """
    if not rut:
        return False
    
    # Remover puntos y guiones, convertir a mayúsculas
    rut = rut.replace(".", "").replace("-", "").upper()
    
    # Verificar formato: al menos 8 caracteres, último puede ser K
    if len(rut) < 8:
        return False
    
    # Separar número y dígito verificador
    numero = rut[:-1]
    dv = rut[-1]
    
    # Verificar que el número sea numérico
    if not numero.isdigit():
        return False
    
    # Calcular dígito verificador
    suma = 0
    multiplicador = 2
    
    for digit in reversed(numero):
        suma += int(digit) * multiplicador
        multiplicador += 1
        if multiplicador > 7:
            multiplicador = 2
    
    resto = suma % 11
    dv_calculado = 11 - resto
    
    if dv_calculado == 11:
        dv_esperado = "0"
    elif dv_calculado == 10:
        dv_esperado = "K"
    else:
        dv_esperado = str(dv_calculado)
    
    return dv == dv_esperado

def validate_email(email: str) -> bool:
    """
    Validar formato básico de email
    
    Args:
        email: String con el email a validar
        
    Returns:
        True si el formato es válido
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_year(year: str) -> bool:
    """
    Validar año académico
    
    Args:
        year: String con el año a validar
        
    Returns:
        True si el año es válido
    """
    if not year:
        return False
    
    try:
        year_int = int(year)
        return 2000 <= year_int <= 2030  # Rango razonable de años
    except ValueError:
        return False

def validate_phone(phone: str) -> bool:
    """
    Validar formato básico de teléfono chileno
    
    Args:
        phone: String con el teléfono a validar
        
    Returns:
        True si el formato es válido
    """
    if not phone:
        return False
    
    # Remover espacios, guiones y paréntesis
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Teléfono chileno: 8-9 dígitos, puede empezar con +56
    if clean_phone.startswith('+56'):
        clean_phone = clean_phone[3:]
    
    return clean_phone.isdigit() and 8 <= len(clean_phone) <= 9

def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
    """
    Limpiar y sanitizar string
    
    Args:
        text: Texto a limpiar
        max_length: Longitud máxima permitida (opcional)
        
    Returns:
        Texto limpio
    """
    if not text:
        return ""
    
    # Remover espacios extras
    text = ' '.join(text.split())
    
    # Truncar si es necesario
    if max_length and len(text) > max_length:
        text = text[:max_length].strip()
    
    return text

def is_valid_profile(profile_value: str) -> bool:
    """
    Validar si el valor de perfil es válido
    
    Args:
        profile_value: Valor del perfil a validar
        
    Returns:
        True si el perfil es válido
    """
    valid_profiles = ['1', '2', '3', '4']
    return profile_value in valid_profiles