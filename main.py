"""
CRM XTART - Cliente de Escritorio
Punto de entrada principal de la aplicación Tkinter
"""

import sys
import tkinter as tk
import ttkbootstrap as tb

from src.api.rest_client import RESTClient
from src.utils.settings import Settings
from src.ui.login_window import LoginWindow
from src.utils.styles import configure_styles


def main():
    """Punto de entrada principal de la aplicación"""

    root = tb.Window(themename="cosmo")
    root.withdraw()

    configure_styles()

    # Crear cliente REST con configuración desde settings
    api_client = RESTClient(
        base_url=Settings.get_api_url(),
        timeout=Settings.get_timeout()
    )

    print(f"[MODO REST] Conectando a {Settings.get_api_url()}")

    # Mostrar ventana de Login
    login_window = LoginWindow(root, api_client)
    login_window.show()

    root.mainloop()


if __name__ == "__main__":
    main()
