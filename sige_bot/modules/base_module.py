"""
Clase base para todos los módulos de descarga
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from core.selenium_manager import SeleniumManager
from core.logger import Logger

class BaseModule(ABC):
    """Clase base abstracta para módulos de descarga"""
    
    def __init__(self, selenium_manager: SeleniumManager, logger: Logger):
        self.selenium_manager = selenium_manager
        self.logger = logger
        self.module_name = self.__class__.__name__
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """Nombre para mostrar en la interfaz"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Descripción del módulo"""
        pass
    
    @property
    def requires_year(self) -> bool:
        """Si el módulo requiere selección de año"""
        return False
    
    @property
    def additional_parameters(self) -> Dict[str, Any]:
        """Parámetros adicionales que requiere el módulo"""
        return {}
    
    def validate_parameters(self, **kwargs) -> bool:
        """
        Validar parámetros antes de ejecutar
        
        Args:
            **kwargs: Parámetros a validar
            
        Returns:
            True si los parámetros son válidos
        """
        if self.requires_year:
            year = kwargs.get('year')
            if not year or not str(year).isdigit():
                self.logger.error(f"Año inválido para {self.display_name}: {year}")
                return False
        
        return True
    
    @abstractmethod
    def execute(self, usuario: str, **kwargs) -> bool:
        """
        Ejecutar la descarga del módulo
        
        Args:
            usuario: Usuario/RBD del establecimiento
            **kwargs: Parámetros adicionales específicos del módulo
            
        Returns:
            True si la ejecución fue exitosa
        """
        pass
    
    def pre_execute(self, **kwargs) -> bool:
        """
        Acciones a realizar antes de la ejecución
        
        Args:
            **kwargs: Parámetros del módulo
            
        Returns:
            True si las pre-acciones fueron exitosas
        """
        self.logger.info(f"🔄 Iniciando módulo: {self.display_name}")
        return self.validate_parameters(**kwargs)
    
    def post_execute(self, success: bool, **kwargs) -> None:
        """
        Acciones a realizar después de la ejecución
        
        Args:
            success: Si la ejecución fue exitosa
            **kwargs: Parámetros del módulo
        """
        if success:
            self.logger.success(f"✅ Módulo {self.display_name} completado exitosamente")
        else:
            self.logger.error(f"❌ Error en módulo {self.display_name}")
    
    def run(self, usuario: str, **kwargs) -> bool:
        """
        Ejecutar el módulo completo con pre y post procesamiento
        
        Args:
            usuario: Usuario/RBD del establecimiento
            **kwargs: Parámetros adicionales específicos del módulo
            
        Returns:
            True si todo el proceso fue exitoso
        """
        try:
            # Pre-ejecución
            if not self.pre_execute(**kwargs):
                return False
            
            # Ejecución principal
            success = self.execute(usuario, **kwargs)
            
            # Post-ejecución
            self.post_execute(success, **kwargs)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error inesperado en {self.display_name}: {str(e)}")
            self.post_execute(False, **kwargs)
            return False