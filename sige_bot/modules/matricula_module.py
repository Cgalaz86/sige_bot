"""
Módulo para descargar información de matrícula
"""
import os
import time
import shutil
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC

from modules.base_module import BaseModule
from config.settings import DOWNLOADS_DIR
from utils.file_utils import generate_unique_filename

class MatriculaModule(BaseModule):
    """Módulo para exportar datos de matrícula"""
    
    @property
    def display_name(self) -> str:
        return "Matrícula"
    
    @property
    def description(self) -> str:
        return "Exporta la nómina de matrícula del establecimiento"
    
    @property
    def requires_year(self) -> bool:
        return True
    
    def execute(self, usuario: str, **kwargs) -> bool:
        """
        Exportar matrícula del establecimiento
        
        Args:
            usuario: RBD del establecimiento
            **kwargs: Debe contener 'year' (año de exportación)
            
        Returns:
            True si la exportación fue exitosa
        """
        year = kwargs.get('year', '2025')
        
        try:
            # Navegar a Administración de Matrícula
            if not self.selenium_manager.navigate_to_section("Adm. Matrícula"):
                return False
            
            # Buscar y hacer clic en el botón de Excel
            excel_button = self.selenium_manager.get_element(
                By.XPATH, "//img[contains(@src,'Excel.GIF')]"
            )
            if not excel_button:
                self.logger.error("No se encontró el botón de Excel")
                return False
            
            excel_button.click()
            
            # Esperar a que cargue la página de exportación
            self.selenium_manager.wait.until(EC.url_contains("ExportarNomina"))
            
            # Seleccionar el año
            year_select = self.selenium_manager.get_element(By.ID, "cmbAno")
            if year_select:
                Select(year_select).select_by_value(str(year))
                self.logger.info(f"Año seleccionado: {year}")
            else:
                self.logger.warning("No se pudo seleccionar el año")
            
            # Hacer clic en el botón EXCEL para descargar
            download_button = self.selenium_manager.get_element(
                By.XPATH, "//a[contains(text(),'EXCEL')]"
            )
            if not download_button:
                self.logger.error("No se encontró el botón de descarga EXCEL")
                return False
            
            download_button.click()
            
            # Manejar posibles alertas
            self.selenium_manager._handle_alerts(timeout=3)
            
            # Esperar que se descargue el archivo
            return self._wait_and_rename_file(usuario, year)
            
        except Exception as e:
            self.logger.error(f"Error exportando matrícula: {str(e)}")
            return False
    
    def _wait_and_rename_file(self, usuario: str, year: str) -> bool:
        """
        Esperar que se descargue el archivo y renombrarlo
        
        Args:
            usuario: RBD del establecimiento
            year: Año de la matrícula
            
        Returns:
            True si el archivo se procesó correctamente
        """
        downloads_folder = DOWNLOADS_DIR
        matricula_folder = downloads_folder / "matricula"
        matricula_folder.mkdir(exist_ok=True)
        
        # Archivo original que descarga SIGE
        original_file = downloads_folder / "nomina_excel.xls"
        
        # Esperar hasta 30 segundos por el archivo
        timeout = time.time() + 30
        while not original_file.exists():
            if time.time() > timeout:
                self.logger.error("❌ Timeout esperando descarga del archivo de matrícula")
                return False
            time.sleep(1)
        
        # Generar nombre único para el archivo
        fecha_hoy = datetime.now().strftime("%Y%m%d")
        base_name = f"matricula_{usuario}_{year}_{fecha_hoy}"
        
        destination_file = generate_unique_filename(
            matricula_folder, base_name, ".xls"
        )
        
        try:
            # Mover archivo a carpeta específica con nombre único
            shutil.move(str(original_file), str(destination_file))
            self.logger.success(f"📥 Matrícula exportada: {destination_file.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error moviendo archivo de matrícula: {str(e)}")
            return False