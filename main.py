"""
CRM XTART - Cliente de Escritorio
Punto de entrada principal de la aplicación Tkinter
"""

import sys
import tkinter as tk

from src.api.rest_client import RESTClient
from src.api.demo_client import DemoClient
from src.ui.login_window import LoginWindow
from src.utils.styles import configure_styles


def main():
    """Punto de entrada principal de la aplicación"""

    import ttkbootstrap as tb

    root = tb.Window(themename="cosmo")

    root.withdraw()

    configure_styles()

    # -------------------------------------------------
    # Selección de modo: Connection (Java) o DEMO (JSON)
    # -------------------------------------------------
    #   Modo DEMO:  python main.py --demo
    #   Modo Connection:  python main.py
    # -------------------------------------------------

    if "--demo" in sys.argv:
        api_client = DemoClient()
        print("[MODO DEMO ACTIVADO] Usando DemoClient")
    else:
        api_client = RESTClient()
        print("[MODO REAL ACTIVADO] Usando RESTClient")

    # -------------------------------------------------
    # Mostrar ventana de Login
    # -------------------------------------------------
    login_window = LoginWindow(root, api_client)
    login_window.show()

    root.mainloop()

if __name__ == "__main__":
    main()
