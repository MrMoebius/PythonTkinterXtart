"""
Configuración de estilos y temas
"""

import tkinter as tk
from tkinter import ttk

def configure_styles():
    """Configura los estilos del tema claro"""
    style = ttk.Style()
    
    # Tema claro
    style.theme_use('clam')
    
    # Configurar estilo para campos inválidos
    style.configure("Invalid.TEntry", 
                   fieldbackground="#f8d7da",
                   bordercolor="#dc3545")
    
    # Configurar estilos de botones
    style.configure("TButton", padding=5)
    
    # Configurar estilos de labels
    style.configure("TLabel", background="white")
    
    # Configurar estilos de frames
    style.configure("TFrame", background="white")
    style.configure("TLabelframe", background="white")
    style.configure("TLabelframe.Label", background="white")

