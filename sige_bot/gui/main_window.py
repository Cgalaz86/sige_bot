"""
Ventana principal de la aplicación
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List

from config.settings import AVAILABLE_PROFILES, AVAILABLE_YEARS, DEFAULT_YEAR
from core.data_storage import DataStorage, ConnectionData
from core.logger import Logger
from core.selenium_manager import SeleniumManager
from modules.matricula_module import MatriculaModule
from modules.datos_colegio_module import DatosColegioModule

class MainWindow:
    """Ventana principal de la aplicación SIGE Bot"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        
        # Componentes del sistema
        self.logger = Logger("SIGE_Bot")
        self.selenium_manager = None
        
        # Módulos disponibles
        self.available_modules = {}
        self.module_vars = {}
        
        # Variables de la interfaz
        self.setup_variables()
        
        # Crear interfaz
        self.create_widgets()
        
        # Configurar logger para mostrar en GUI
        self.logger.set_gui_callback(self.log_to_gui)
        
        # Cargar módulos
        self.load_modules()
        
        # Cargar datos guardados
        self.refresh_saved_connections()
    
    def setup_window(self):
        """Configurar la ventana principal"""
        self.root.title("SIGE Bot - Descarga de Información")
        self.root.geometry("1000x650")
        self.root.minsize(900, 600)
        
        # Configurar estilo
        self.root.configure(bg='#f0f0f0')
        
        # Configurar el estilo de ttk
        style = ttk.Style()
        style.theme_use('clam')  # Tema más moderno
    
    def setup_variables(self):
        """Configurar variables de tkinter"""
        self.var_usuario = tk.StringVar()
        self.var_clave = tk.StringVar()
        self.var_perfil = tk.StringVar()
        self.var_conexion_guardada = tk.StringVar()
        self.var_anio = tk.StringVar(value=DEFAULT_YEAR)
    
    def create_widgets(self):
        """Crear todos los widgets de la interfaz"""
        # Frame principal dividido en dos
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Panel izquierdo (controles) - ancho fijo
        left_panel = ttk.LabelFrame(main_frame, text=" 🔧 Configuración ", padding="15")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        left_panel.configure(width=350)  # Ancho fijo para evitar problemas de layout
        
        # Panel derecho (logs)
        right_panel = ttk.LabelFrame(main_frame, text=" 📋 Registro de Actividad ", padding="15")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Crear secciones del panel izquierdo
        self.create_login_section(left_panel)
        self.create_modules_section(left_panel)
        self.create_actions_section(left_panel)
        
        # Crear sección de logs
        self.create_logs_section(right_panel)
    
    def create_login_section(self, parent):
        """Crear sección de login"""
        login_frame = ttk.LabelFrame(parent, text=" 🔐 Credenciales ", padding="10")
        login_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Usuario
        ttk.Label(login_frame, text="Usuario (RBD/RUT):").grid(row=0, column=0, sticky="w", pady=3)
        self.entry_usuario = ttk.Entry(login_frame, textvariable=self.var_usuario, width=25)
        self.entry_usuario.grid(row=0, column=1, sticky="ew", pady=3, padx=(10, 0))
        
        # Contraseña
        ttk.Label(login_frame, text="Contraseña:").grid(row=1, column=0, sticky="w", pady=3)
        self.entry_clave = ttk.Entry(login_frame, textvariable=self.var_clave, show="*", width=25)
        self.entry_clave.grid(row=1, column=1, sticky="ew", pady=3, padx=(10, 0))
        
        # Perfil
        ttk.Label(login_frame, text="Perfil:").grid(row=2, column=0, sticky="w", pady=3)
        self.combo_perfil = ttk.Combobox(login_frame, textvariable=self.var_perfil, 
                                         values=list(AVAILABLE_PROFILES.values()), 
                                         state="readonly", width=22)
        self.combo_perfil.grid(row=2, column=1, sticky="ew", pady=3, padx=(10, 0))
        
        # Separador
        separator = ttk.Separator(login_frame, orient="horizontal")
        separator.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 10))
        
        # Conexiones guardadas
        ttk.Label(login_frame, text="Conexiones guardadas:").grid(row=4, column=0, sticky="w", pady=3)
        self.combo_conexiones = ttk.Combobox(login_frame, textvariable=self.var_conexion_guardada,
                                             state="readonly", width=22)
        self.combo_conexiones.grid(row=4, column=1, sticky="ew", pady=3, padx=(10, 0))
        self.combo_conexiones.bind("<<ComboboxSelected>>", self.on_connection_selected)
        
        # Configurar expansión de columnas
        login_frame.columnconfigure(1, weight=1)
    
    def create_modules_section(self, parent):
        """Crear sección de selección de módulos"""
        modules_frame = ttk.LabelFrame(parent, text=" 📦 Módulos de Descarga ", padding="10")
        modules_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Frame contenedor para los checkboxes de módulos
        self.modules_container = ttk.Frame(modules_frame)
        self.modules_container.pack(fill=tk.X, pady=(0, 10))
        
        # Separador visual
        separator = ttk.Separator(modules_frame, orient="horizontal")
        separator.pack(fill=tk.X, pady=(10, 10))
        
        # Frame para año
        year_frame = ttk.Frame(modules_frame)
        year_frame.pack(fill=tk.X)
        
        ttk.Label(year_frame, text="Año académico:").pack(side=tk.LEFT)
        self.combo_anio = ttk.Combobox(year_frame, textvariable=self.var_anio,
                                       values=[str(year) for year in AVAILABLE_YEARS],
                                       state="readonly", width=8)
        self.combo_anio.pack(side=tk.RIGHT)
    
    def create_actions_section(self, parent):
        """Crear sección de acciones"""
        actions_frame = ttk.LabelFrame(parent, text=" ⚡ Acciones ", padding="10")
        actions_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botón principal de ejecución
        self.btn_ejecutar = ttk.Button(actions_frame, text="🚀 Iniciar Descarga",
                                       command=self.execute_download)
        self.btn_ejecutar.pack(fill=tk.X, pady=(0, 8))
        
        # Botón de actualizar conexiones
        btn_refresh = ttk.Button(actions_frame, text="🔄 Actualizar Conexiones",
                                 command=self.refresh_saved_connections)
        btn_refresh.pack(fill=tk.X, pady=(0, 8))
        
        # Botón de salir
        btn_salir = ttk.Button(actions_frame, text="❌ Salir", command=self.root.quit)
        btn_salir.pack(fill=tk.X)
    
    def create_logs_section(self, parent):
        """Crear sección de logs"""
        # Área de texto para logs
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_logs = tk.Text(text_frame, width=50, height=25, wrap="word",
                                 font=("Consolas", 9))
        
        # Scrollbar para logs
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_logs.yview)
        self.text_logs.configure(yscrollcommand=scrollbar.set)
        
        self.text_logs.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botón para limpiar logs
        btn_clear = ttk.Button(parent, text="🗑️ Limpiar Logs", command=self.clear_logs)
        btn_clear.pack(pady=(5, 0))
    
    def load_modules(self):
        """Cargar y configurar módulos disponibles"""
        # Inicializar selenium manager (sin conectar aún)
        self.selenium_manager = SeleniumManager(self.logger)
        
        # Registrar módulos disponibles
        self.available_modules = {
            'matricula': MatriculaModule(self.selenium_manager, self.logger),
            'datos_colegio': DatosColegioModule(self.selenium_manager, self.logger)
        }
        
        # Crear checkboxes para cada módulo en el contenedor correcto
        row = 0
        for module_key, module in self.available_modules.items():
            var = tk.BooleanVar()
            self.module_vars[module_key] = var
            
            checkbox = ttk.Checkbutton(self.modules_container, 
                                       text=f"📋 {module.display_name}",
                                       variable=var)
            checkbox.grid(row=row, column=0, sticky="w", pady=2)
            
            # Tooltip con descripción
            self.create_tooltip(checkbox, module.description)
            row += 1
        
        # Configurar el grid del contenedor
        self.modules_container.columnconfigure(0, weight=1)
    
    def create_tooltip(self, widget, text):
        """Crear tooltip para un widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            
            label = tk.Label(tooltip, text=text, background="lightyellow",
                           relief="solid", borderwidth=1, font=("Arial", 8))
            label.pack()
            
            def hide_tooltip():
                tooltip.destroy()
            
            tooltip.after(3000, hide_tooltip)  # Auto-hide after 3 seconds
        
        widget.bind("<Enter>", show_tooltip)
    
    def refresh_saved_connections(self):
        """Actualizar lista de conexiones guardadas"""
        connections = DataStorage.get_connection_strings()
        
        # Crear lista más legible para mostrar
        display_connections = []
        for conn_str in connections:
            conn_data = DataStorage.parse_connection_string(conn_str)
            if conn_data:
                profile_name = AVAILABLE_PROFILES.get(conn_data.perfil, f"Perfil {conn_data.perfil}")
                display_text = f"{conn_data.usuario} ({profile_name})"
                display_connections.append(display_text)
        
        self.combo_conexiones['values'] = display_connections
        self._connection_mapping = dict(zip(display_connections, connections))
    
    def on_connection_selected(self, event=None):
        """Manejar selección de conexión guardada"""
        selected_display = self.var_conexion_guardada.get()
        if not selected_display:
            return
        
        # Obtener string de conexión original
        connection_string = self._connection_mapping.get(selected_display)
        if not connection_string:
            return
        
        # Parsear y cargar datos
        conn_data = DataStorage.parse_connection_string(connection_string)
        if conn_data:
            self.var_usuario.set(conn_data.usuario)
            self.var_clave.set(conn_data.clave)
            
            # Establecer perfil
            profile_name = AVAILABLE_PROFILES.get(conn_data.perfil, "")
            self.var_perfil.set(profile_name)
    
    def validate_input(self) -> bool:
        """Validar datos de entrada"""
        if not self.var_usuario.get().strip():
            messagebox.showerror("Error", "Por favor ingrese el usuario (RBD/RUT)")
            return False
        
        if not self.var_clave.get().strip():
            messagebox.showerror("Error", "Por favor ingrese la contraseña")
            return False
        
        if not self.var_perfil.get():
            messagebox.showerror("Error", "Por favor seleccione un perfil")
            return False
        
        # Verificar que al menos un módulo esté seleccionado
        selected_modules = [key for key, var in self.module_vars.items() if var.get()]
        if not selected_modules:
            messagebox.showerror("Error", "Por favor seleccione al menos un módulo para descargar")
            return False
        
        return True
    
    def execute_download(self):
        """Ejecutar proceso de descarga"""
        if not self.validate_input():
            return
        
        # Deshabilitar botón durante ejecución
        self.btn_ejecutar.config(state="disabled", text="🔄 Procesando...")
        
        try:
            # Obtener datos
            usuario = self.var_usuario.get().strip()
            clave = self.var_clave.get().strip()
            perfil_name = self.var_perfil.get()
            
            # Obtener valor de perfil
            perfil_valor = None
            for key, value in AVAILABLE_PROFILES.items():
                if value == perfil_name:
                    perfil_valor = key
                    break
            
            if not perfil_valor:
                messagebox.showerror("Error", "Perfil no válido")
                return
            
            # Guardar conexión
            DataStorage.save_connection(usuario, clave, perfil_valor)
            self.refresh_saved_connections()
            
            # Realizar login
            if not self.selenium_manager.login(usuario, clave, perfil_valor):
                messagebox.showerror("Error", "No se pudo iniciar sesión")
                return
            
            # Ejecutar módulos seleccionados
            selected_modules = [key for key, var in self.module_vars.items() if var.get()]
            success_count = 0
            
            for module_key in selected_modules:
                module = self.available_modules[module_key]
                
                # Preparar parámetros
                kwargs = {}
                if module.requires_year:
                    kwargs['year'] = self.var_anio.get()
                
                # Ejecutar módulo
                if module.run(usuario, **kwargs):
                    success_count += 1
            
            # Mostrar resumen
            total_modules = len(selected_modules)
            if success_count == total_modules:
                self.logger.success(f"✅ Proceso completado exitosamente. {success_count}/{total_modules} módulos ejecutados.")
                messagebox.showinfo("Éxito", f"Se completaron exitosamente {success_count} de {total_modules} descargas.")
            else:
                self.logger.warning(f"⚠ Proceso completado con errores. {success_count}/{total_modules} módulos ejecutados.")
                messagebox.showwarning("Advertencia", f"Solo se completaron {success_count} de {total_modules} descargas.")
        
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            self.logger.error(error_msg)
            messagebox.showerror("Error", error_msg)
        
        finally:
            # Cerrar selenium
            if self.selenium_manager:
                self.selenium_manager.close()
            
            # Rehabilitar botón
            self.btn_ejecutar.config(state="normal", text="🚀 Iniciar Descarga")
    
    def log_to_gui(self, message: str):
        """Callback para mostrar logs en la interfaz"""
        self.text_logs.insert(tk.END, message + "\n")
        self.text_logs.see(tk.END)
        self.root.update_idletasks()
    
    def clear_logs(self):
        """Limpiar el área de logs"""
        self.text_logs.delete(1.0, tk.END)
    
    def run(self):
        """Ejecutar la aplicación"""
        self.root.mainloop()