"""
Gestor centralizado para operaciones de Selenium
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchWindowException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from config.settings import (
    SIGE_LOGIN_URL, SELENIUM_TIMEOUT, MAX_LOGIN_ATTEMPTS, 
    CHROME_DRIVER_PATH, DOWNLOADS_DIR
)
from core.logger import Logger

class SeleniumManager:
    """Gestor de operaciones Selenium para SIGE"""
    
    def __init__(self, logger: Logger):
        self.driver = None
        self.wait = None
        self.logger = logger
        self.is_logged_in = False
        
    def initialize_driver(self):
        """Inicializar el driver de Chrome con configuraciones"""
        self.logger.log("🚀 Iniciando navegador Chrome...")
        
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {
            "download.default_directory": str(DOWNLOADS_DIR)
        })
        
        # Opcional: ejecutar en modo headless
        # options.add_argument("--headless")
        
        service = Service(CHROME_DRIVER_PATH)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, SELENIUM_TIMEOUT)
        
    def login(self, usuario: str, clave: str, perfil_valor: str) -> bool:
        """
        Realizar login en SIGE
        
        Args:
            usuario: RBD o RUT del sostenedor
            clave: Contraseña
            perfil_valor: Valor del perfil (1-4)
            
        Returns:
            bool: True si el login fue exitoso
        """
        if not self.driver:
            self.initialize_driver()
            
        for intento in range(1, MAX_LOGIN_ATTEMPTS + 1):
            try:
                self.logger.log(f"Intento {intento}: navegando al login...")
                self.driver.get(SIGE_LOGIN_URL)
                
                # Llenar formulario de login
                campo_usuario = self.wait.until(
                    EC.presence_of_element_located((By.ID, "usuario"))
                )
                campo_clave = self.driver.find_element(By.ID, "clave")
                select_perfil = Select(self.driver.find_element(By.ID, "perfil"))
                
                campo_usuario.clear()
                campo_usuario.send_keys(usuario)
                campo_clave.clear()
                campo_clave.send_keys(clave)
                select_perfil.select_by_value(perfil_valor)
                
                # Enviar formulario
                self.driver.execute_script("enviar();")
                
                # Verificar si hay alertas de error
                if self._handle_alerts():
                    self.logger.log("❌ Error al iniciar sesión. Reintentando...")
                    continue
                
                # Verificar login exitoso
                try:
                    self.wait.until(
                        EC.presence_of_element_located((By.LINK_TEXT, "Adm. Matrícula"))
                    )
                    self.logger.log("✅ Login exitoso.")
                    self._close_initial_popup()
                    self.is_logged_in = True
                    return True
                    
                except TimeoutException:
                    self.logger.log("⚠ No apareció menú después de login, reintentando...")
                    continue
                    
            except (NoSuchWindowException, Exception) as e:
                self.logger.log(f"❌ Error en intento {intento}: {str(e)}")
                break
                
        self.logger.log("❌ No se pudo iniciar sesión después de todos los intentos.")
        return False
    
    def _handle_alerts(self, timeout: int = 3) -> bool:
        """
        Manejar alertas automáticamente
        
        Args:
            timeout: Tiempo de espera para detectar alerta
            
        Returns:
            bool: True si se detectó y cerró una alerta
        """
        try:
            WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            self.logger.log(f"⚠ Alerta detectada: {alert.text}")
            alert.accept()
            self.logger.log("✔ Alerta cerrada automáticamente.")
            return True
        except TimeoutException:
            return False
    
    def _close_initial_popup(self):
        """Cerrar popup inicial que aparece después del login"""
        try:
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ui-widget-overlay"))
            )
            self.logger.log("⚠ Popup detectado.")
            
            try:
                boton_cerrar = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((
                        By.XPATH, 
                        "//div[contains(@class,'ui-dialog')]//button[contains(text(),'Cerrar')]"
                    ))
                )
                boton_cerrar.click()
                self.logger.log("✔ Popup cerrado con botón.")
            except Exception:
                self.logger.log("⚠ Cerrando popup con ESC...")
                ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            
            WebDriverWait(self.driver, 5).until_not(
                EC.presence_of_element_located((By.CLASS_NAME, "ui-widget-overlay"))
            )
        except TimeoutException:
            self.logger.log("✔ No hubo popup inicial.")
    
    def navigate_to_section(self, section_name: str) -> bool:
        """
        Navegar a una sección específica del menú
        
        Args:
            section_name: Nombre de la sección del menú
            
        Returns:
            bool: True si la navegación fue exitosa
        """
        if not self.is_logged_in:
            self.logger.log("❌ No hay sesión activa.")
            return False
            
        try:
            self.logger.log(f"➡ Navegando a '{section_name}'...")
            link = self.wait.until(
                EC.element_to_be_clickable((By.LINK_TEXT, section_name))
            )
            link.click()
            return True
        except TimeoutException:
            self.logger.log(f"❌ No se pudo navegar a '{section_name}'")
            return False
    
    def get_element(self, locator_type: By, locator_value: str, timeout: int = None):
        """
        Obtener elemento con manejo de errores
        
        Args:
            locator_type: Tipo de localizador (By.ID, By.XPATH, etc.)
            locator_value: Valor del localizador
            timeout: Tiempo de espera personalizado
            
        Returns:
            WebElement o None si no se encuentra
        """
        wait_time = timeout or SELENIUM_TIMEOUT
        try:
            wait = WebDriverWait(self.driver, wait_time)
            return wait.until(EC.presence_of_element_located((locator_type, locator_value)))
        except TimeoutException:
            self.logger.log(f"⚠ Elemento no encontrado: {locator_value}")
            return None
    
    def close(self):
        """Cerrar el navegador"""
        if self.driver:
            self.logger.log("🔒 Cerrando navegador...")
            self.driver.quit()
            self.driver = None
            self.wait = None
            self.is_logged_in = False