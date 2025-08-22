"""
Módulo para exportar datos generales del colegio
"""
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from openpyxl import Workbook

from modules.base_module import BaseModule
from config.settings import DOWNLOADS_DIR
from utils.file_utils import generate_unique_filename

class DatosColegioModule(BaseModule):
    """Módulo para exportar datos generales del establecimiento"""
    
    @property
    def display_name(self) -> str:
        return "Datos del Colegio"
    
    @property
    def description(self) -> str:
        return "Exporta los datos generales del establecimiento"
    
    def execute(self, usuario: str, **kwargs) -> bool:
        """
        Exportar datos generales del establecimiento
        
        Args:
            usuario: RBD del establecimiento
            **kwargs: Parámetros adicionales (no requeridos para este módulo)
            
        Returns:
            True si la exportación fue exitosa
        """
        try:
            # Navegar a Datos Generales
            if not self.selenium_manager.navigate_to_section("Datos Generales"):
                return False
            
            # Esperar a que cargue la página
            self.selenium_manager.wait.until(EC.url_contains("FichaEstab"))
            
            # Extraer datos del formulario
            datos = self._extract_school_data()
            
            # Guardar en archivo Excel
            return self._save_to_excel(usuario, datos)
            
        except Exception as e:
            self.logger.error(f"Error exportando datos del colegio: {str(e)}")
            return False
    
    def _extract_school_data(self) -> dict:
        """
        Extraer datos del formulario de datos generales
        
        Returns:
            Diccionario con los datos extraídos
        """
        datos = {}
        driver = self.selenium_manager.driver
        
        try:
            # Nombre del colegio (texto plano en celda de tabla)
            nombre_element = driver.find_element(
                By.XPATH, "//td[text()='Nombre :']/following-sibling::td"
            )
            datos["Nombre"] = nombre_element.text.strip() if nombre_element else ""
        except:
            datos["Nombre"] = ""
            self.logger.warning("No se pudo extraer el nombre del colegio")
        
        # Mapeo de campos de input
        campos_input = {
            "N° Res. RECOFI/ N° Docto. Traspaso": "txtRes",
            "Fecha Resolución": "txtFecha",
            "Dirección Calle": "txtDirEstab",
            "Número": "txtDirNum",
            "E-mail": "txtMailEsta",
            "RUN Director": "txtRunDir",
            "Nombre Director": "txtNombreDir",
            "Ap Paterno Director": "txtNombreDir2",
            "Ap Materno Director": "txtNombreDir3",
            "E-mail Director": "txtMail"
        }
        
        # Extraer datos de campos de input
        for etiqueta, campo_id in campos_input.items():
            try:
                element = driver.find_element(By.ID, campo_id)
                datos[etiqueta] = element.get_attribute("value").strip() if element else ""
            except:
                datos[etiqueta] = ""
                self.logger.warning(f"No se pudo extraer {etiqueta}")
        
        # Teléfono (combinación de área y número)
        try:
            area = driver.find_element(By.ID, "txtAreaEstab").get_attribute("value")
            numero = driver.find_element(By.ID, "txtFonoEstab").get_attribute("value")
            datos["Fono"] = f"{area}-{numero}" if area and numero else ""
        except:
            datos["Fono"] = ""
            self.logger.warning("No se pudo extraer teléfono")
        
        # Celular (combinación de prefijo y número)
        try:
            prefijo = driver.find_element(By.ID, "pre-cel").get_attribute("value")
            celular = driver.find_element(By.ID, "txtCel").get_attribute("value")
            datos["Celular"] = f"{prefijo}-{celular}" if prefijo and celular else ""
        except:
            datos["Celular"] = ""
            self.logger.warning("No se pudo extraer celular")
        
        # Género del alumnado (select)
        try:
            select_genero = Select(driver.find_element(By.ID, "tipoAlumnado"))
            datos["Género"] = select_genero.first_selected_option.text.strip()
        except:
            datos["Género"] = ""
            self.logger.warning("No se pudo extraer género del alumnado")
        
        self.logger.info(f"Datos extraídos: {len([v for v in datos.values() if v])} campos con información")
        return datos
    
    def _save_to_excel(self, usuario: str, datos: dict) -> bool:
        """
        Guardar datos en archivo Excel
        
        Args:
            usuario: RBD del establecimiento
            datos: Diccionario con los datos extraídos
            
        Returns:
            True si se guardó correctamente
        """
        try:
            # Crear carpeta específica
            colegio_folder = DOWNLOADS_DIR / "datos_colegio"
            colegio_folder.mkdir(exist_ok=True)
            
            # Generar nombre único
            fecha_hoy = datetime.now().strftime("%Y%m%d")
            base_name = f"colegio_{usuario}_{fecha_hoy}"
            
            archivo_destino = generate_unique_filename(
                colegio_folder, base_name, ".xlsx"
            )
            
            # Crear workbook
            wb = Workbook()
            ws = wb.active
            ws.title = "Datos Colegio"
            
            # Agregar headers
            headers = ["RBD"] + list(datos.keys())
            ws.append(headers)
            
            # Agregar fila de datos
            fila_datos = [usuario] + list(datos.values())
            ws.append(fila_datos)
            
            # Ajustar ancho de columnas
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)  # Máximo 50 caracteres
                ws.column_dimensions[column_letter].width = adjusted_width
            
            # Guardar archivo
            wb.save(archivo_destino)
            self.logger.success(f"📥 Datos del colegio exportados: {archivo_destino.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error guardando datos del colegio: {str(e)}")
            return False