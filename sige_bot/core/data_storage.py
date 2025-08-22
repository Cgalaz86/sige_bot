"""
Gestión de almacenamiento de datos de conexión
"""
from typing import List, Tuple, Optional
from dataclasses import dataclass
from config.settings import CONNECTIONS_FILE

@dataclass
class ConnectionData:
    """Datos de conexión guardados"""
    usuario: str
    clave: str
    perfil: str
    
    def __str__(self):
        return f"{self.usuario},{self.clave},{self.perfil}"

class DataStorage:
    """Gestor de almacenamiento de credenciales"""
    
    @staticmethod
    def save_connection(usuario: str, clave: str, perfil_valor: str) -> None:
        """
        Guardar o actualizar datos de conexión
        
        Args:
            usuario: RBD o RUT del sostenedor
            clave: Contraseña
            perfil_valor: Valor del perfil (1-4)
        """
        connections = DataStorage.load_connections()
        
        # Buscar si ya existe la conexión
        updated = False
        for i, conn in enumerate(connections):
            if conn.usuario == usuario:
                connections[i] = ConnectionData(usuario, clave, perfil_valor)
                updated = True
                break
        
        # Si no existe, agregar nueva conexión
        if not updated:
            connections.append(ConnectionData(usuario, clave, perfil_valor))
        
        # Guardar todas las conexiones
        DataStorage._write_connections(connections)
    
    @staticmethod
    def load_connections() -> List[ConnectionData]:
        """
        Cargar todas las conexiones guardadas
        
        Returns:
            Lista de ConnectionData
        """
        connections = []
        
        if not CONNECTIONS_FILE.exists():
            return connections
        
        try:
            with open(CONNECTIONS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split(",")
                    if len(parts) == 3:
                        connections.append(ConnectionData(*parts))
        
        except Exception as e:
            print(f"Error cargando conexiones: {e}")
        
        return connections
    
    @staticmethod
    def get_connection_strings() -> List[str]:
        """
        Obtener lista de strings de conexiones para mostrar en combobox
        
        Returns:
            Lista de strings con formato "usuario,clave,perfil"
        """
        connections = DataStorage.load_connections()
        return [str(conn) for conn in connections]
    
    @staticmethod
    def find_connection(usuario: str) -> Optional[ConnectionData]:
        """
        Buscar una conexión específica por usuario
        
        Args:
            usuario: Usuario a buscar
            
        Returns:
            ConnectionData si se encuentra, None si no
        """
        connections = DataStorage.load_connections()
        for conn in connections:
            if conn.usuario == usuario:
                return conn
        return None
    
    @staticmethod
    def delete_connection(usuario: str) -> bool:
        """
        Eliminar una conexión específica
        
        Args:
            usuario: Usuario de la conexión a eliminar
            
        Returns:
            True si se eliminó, False si no se encontró
        """
        connections = DataStorage.load_connections()
        original_count = len(connections)
        
        connections = [conn for conn in connections if conn.usuario != usuario]
        
        if len(connections) < original_count:
            DataStorage._write_connections(connections)
            return True
        return False
    
    @staticmethod
    def _write_connections(connections: List[ConnectionData]) -> None:
        """
        Escribir conexiones al archivo
        
        Args:
            connections: Lista de conexiones a guardar
        """
        # Crear directorio padre si no existe
        CONNECTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(CONNECTIONS_FILE, "w", encoding="utf-8") as f:
                for conn in connections:
                    f.write(f"{conn}\n")
        except Exception as e:
            print(f"Error guardando conexiones: {e}")
    
    @staticmethod
    def parse_connection_string(connection_string: str) -> Optional[ConnectionData]:
        """
        Parsear string de conexión a objeto ConnectionData
        
        Args:
            connection_string: String con formato "usuario,clave,perfil"
            
        Returns:
            ConnectionData si el formato es válido, None si no
        """
        try:
            parts = connection_string.split(",")
            if len(parts) == 3:
                return ConnectionData(*parts)
        except Exception:
            pass
        return None