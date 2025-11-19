"""
CRM XTART - Cliente de Escritorio
Aplicación principal para gestionar el sistema CRM XTART
"""

import tkinter as tk
from src.ui.login_window import LoginWindow
from src.utils.styles import configure_styles

def main():
    """Punto de entrada principal de la aplicación"""
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal hasta el login
    
    # Configurar estilos
    configure_styles()
    
    app = LoginWindow(root)
    app.show()
    
    root.mainloop()

if __name__ == "__main__":
    main()

