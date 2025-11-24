"""
Ventana de ayuda y documentación
"""
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from tkinterweb import HtmlFrame
import urllib.parse
import urllib.request
import os

class HelpWindow:
    """Ventana de ayuda contextual"""
    
    def __init__(self, parent):
        self.parent = parent
        self.window = None
    
    def show(self, html_path="docs/ayuda.html"):

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("Ayuda - CRM XTART")
        self.window.geometry("700x450")
        self.window.resizable(True, True)

        # Mantener ventana al frente al abrir
        self.window.attributes("-topmost", True)
        self.window.after(200, lambda: self.window.attributes("-topmost", False))

        # Centrar ventana
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.window.winfo_screenheight() // 2) - (450 // 2)
        self.window.geometry(f"700x450+{x}+{y}")
        
        # Contenedor principal
        wrapper = ctk.CTkFrame(self.window, corner_radius=10)
        wrapper.pack(fill="both", expand=True, padx=10, pady=10)

        # Visor HTML
        html_view = HtmlFrame(wrapper, messages_enabled=False)
        html_view.pack(fill="both", expand=True)

        # -----------------------------------------------------
        # Resolver ruta relativa → absoluta real (automático)
        # -----------------------------------------------------
        
        # Ubicación real de este archivo (help_window.py)
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Subir dos niveles /src/ui → /src → /tkinter
        project_root = os.path.abspath(os.path.join(base_dir, "..", ".."))

        # Ruta final del archivo HTML dentro del proyecto
        final_html_path = os.path.join(project_root, html_path)

        # Convertir a URL válida para tkinterweb
        print("Ruta final HTML:", final_html_path)
        print("Existe HTML:", os.path.exists(final_html_path))

        html_view.load_file(final_html_path)



        # Botón cerrar
        ctk.CTkButton(
            self.window, 
            text="Cerrar", 
            command=self.window.destroy
        ).pack(pady=10)


