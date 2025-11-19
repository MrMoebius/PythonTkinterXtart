"""
Ventana de login y autenticación
"""

import tkinter as tk
from tkinter import ttk, messagebox
from src.api.rest_client import RESTClient
from src.ui.main_window import MainWindow

class LoginWindow:
    """Ventana de inicio de sesión"""
    
    def __init__(self, root):
        self.root = root
        self.api = RESTClient()
        self.window = None
    
    def show(self):
        """Muestra la ventana de login"""
        self.window = tk.Toplevel(self.root)
        self.window.title("CRM XTART - Inicio de Sesión")
        self.window.geometry("400x300")
        self.window.resizable(False, False)
        self.window.transient(self.root)
        self.window.grab_set()
        
        # Centrar ventana
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.window.winfo_screenheight() // 2) - (300 // 2)
        self.window.geometry(f"400x300+{x}+{y}")
        
        self._create_widgets()
        
        # Bind Enter para login
        self.window.bind("<Return>", lambda e: self._login())
    
    def _create_widgets(self):
        """Crea los widgets de la ventana"""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="CRM XTART", 
                               font=("Arial", 20, "bold"))
        title_label.pack(pady=20)
        
        subtitle_label = ttk.Label(main_frame, text="Sistema de Gestión", 
                                  font=("Arial", 10))
        subtitle_label.pack(pady=5)
        
        # Frame de formulario
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(pady=20, fill=tk.X)
        
        # Usuario
        ttk.Label(form_frame, text="Usuario:").grid(row=0, column=0, sticky="w", pady=10, padx=5)
        self.username_entry = ttk.Entry(form_frame, width=30)
        self.username_entry.grid(row=0, column=1, pady=10, padx=5)
        self.username_entry.focus()
        
        # Contraseña
        ttk.Label(form_frame, text="Contraseña:").grid(row=1, column=0, sticky="w", pady=10, padx=5)
        self.password_entry = ttk.Entry(form_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, pady=10, padx=5)
        
        # Botón de login
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        login_button = ttk.Button(button_frame, text="Iniciar Sesión", 
                                 command=self._login, width=20)
        login_button.pack(pady=5)
        
        # Info
        info_label = ttk.Label(main_frame, 
                              text="Ingrese sus credenciales para acceder al sistema",
                              font=("Arial", 8), foreground="gray")
        info_label.pack(pady=10)
    
    def _login(self):
        """Realiza el login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Por favor, complete todos los campos")
            return
        
        # Deshabilitar botón durante el login
        self.window.config(cursor="wait")
        
        result = self.api.login(username, password)
        
        self.window.config(cursor="")
        
        if result["success"]:
            # Cerrar ventana de login
            self.window.destroy()
            
            # Abrir ventana principal
            main_window = MainWindow(self.root, self.api)
            main_window.show()
        else:
            error_msg = result.get("error", "Error desconocido")
            messagebox.showerror("Error de Autenticación", 
                               f"No se pudo iniciar sesión:\n{error_msg}")

