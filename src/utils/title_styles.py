"""
Estilos predefinidos para decorar títulos en el header
"""

import customtkinter as ctk

# ================================================================
# PALETA DE COLORES
# ================================================================
COLORS = {
    # Colores principales
    "primary": "#2491ed",      # Azul principal
    "primary_hover": "#137bd6",
    "secondary": "#6c757d",   # Gris
    "success": "#28a745",      # Verde
    "warning": "#ffc107",      # Amarillo/Naranja
    "danger": "#dc3545",       # Rojo
    "info": "#17a2b8",         # Azul claro
    "purple": "#6f42c1",       # Púrpura
    "pink": "#e83e8c",         # Rosa
    "orange": "#fd7e14",       # Naranja
    
    # Colores del tema oscuro
    "dark_bg": "#23243a",
    "dark_card": "#252932",
    "white": "#ffffff",
    "light_gray": "#ccd3db",
    
    # Gradientes (simulados con colores)
    "gradient_start": "#2491ed",
    "gradient_end": "#6f42c1",
}

# ================================================================
# FUENTES DISPONIBLES
# ================================================================
FONTS = {
    "arial": ("Arial", 32, "bold"),
    "arial_large": ("Arial", 36, "bold"),
    "arial_italic": ("Arial", 32, "bold italic"),
    "segoe": ("Segoe UI", 32, "bold"),
    "roboto": ("Roboto", 32, "bold"),
    "montserrat": ("Montserrat", 32, "bold"),
    "verdana": ("Verdana", 32, "bold"),
    "calibri": ("Calibri", 32, "bold"),
}

# ================================================================
# ESTILOS PREDEFINIDOS
# ================================================================

class TitleStyles:
    """Colección de estilos para títulos"""
    
    @staticmethod
    def style_default():
        """Estilo por defecto: blanco, Arial, bold"""
        return {
            "font": ctk.CTkFont("Arial", 32, "bold"),
            "text_color": COLORS["white"]
        }
    
    @staticmethod
    def style_primary():
        """Estilo primario: azul brillante"""
        return {
            "font": ctk.CTkFont("Arial", 32, "bold"),
            "text_color": COLORS["primary"]
        }
    
    @staticmethod
    def style_gradient_blue_purple():
        """Estilo con color que simula gradiente azul-púrpura"""
        return {
            "font": ctk.CTkFont("Arial", 32, "bold"),
            "text_color": COLORS["gradient_end"]  # Púrpura como color principal
        }
    
    @staticmethod
    def style_purple():
        """Estilo púrpura elegante"""
        return {
            "font": ctk.CTkFont("Arial", 32, "bold"),
            "text_color": COLORS["purple"]
        }
    
    @staticmethod
    def style_orange():
        """Estilo naranja vibrante"""
        return {
            "font": ctk.CTkFont("Arial", 32, "bold"),
            "text_color": COLORS["orange"]
        }
    
    @staticmethod
    def style_with_shadow():
        """Estilo con efecto de sombra (usando color más oscuro)"""
        return {
            "font": ctk.CTkFont("Arial", 32, "bold"),
            "text_color": COLORS["primary"],
            # Nota: CustomTkinter no soporta sombras directamente,
            # pero puedes usar un color más oscuro para simularlo
        }
    
    @staticmethod
    def style_segoe_ui():
        """Estilo con fuente Segoe UI"""
        return {
            "font": ctk.CTkFont("Segoe UI", 32, "bold"),
            "text_color": COLORS["white"]
        }
    
    @staticmethod
    def style_roboto():
        """Estilo con fuente Roboto (si está disponible)"""
        return {
            "font": ctk.CTkFont("Roboto", 32, "bold"),
            "text_color": COLORS["primary"]
        }
    
    @staticmethod
    def style_italic():
        """Estilo con texto en cursiva"""
        return {
            "font": ctk.CTkFont("Arial", 32, "bold italic"),
            "text_color": COLORS["white"]
        }
    
    @staticmethod
    def style_large():
        """Estilo con fuente más grande"""
        return {
            "font": ctk.CTkFont("Arial", 40, "bold"),
            "text_color": COLORS["white"]
        }
    
    @staticmethod
    def style_small():
        """Estilo con fuente más pequeña"""
        return {
            "font": ctk.CTkFont("Arial", 28, "bold"),
            "text_color": COLORS["white"]
        }
    
    @staticmethod
    def style_by_section(section_name: str):
        """Estilo que cambia según la sección"""
        section_colors = {
            "Dashboard": COLORS["primary"],
            "Clientes": COLORS["success"],
            "Empleados": COLORS["info"],
            "Productos": COLORS["warning"],
            "Presupuestos": COLORS["purple"],
            "Facturas": COLORS["danger"],
            "Pagos": COLORS["info"],
            "Informes": COLORS["pink"],
            "Mi Perfil": COLORS["primary"],
            "Mis Facturas": COLORS["danger"],
            "Mis Pagos": COLORS["success"],
            "Mis Presupuestos": COLORS["purple"],
        }
        
        color = section_colors.get(section_name, COLORS["white"])
        return {
            "font": ctk.CTkFont("Arial", 32, "bold"),
            "text_color": color
        }


# ================================================================
# FUNCIÓN HELPER PARA APLICAR ESTILOS
# ================================================================
def apply_title_style(label: ctk.CTkLabel, style_name: str = "default", section_name: str = None):
    """
    Aplica un estilo predefinido al título
    
    Args:
        label: El CTkLabel del título
        style_name: Nombre del estilo ("default", "primary", "purple", etc.)
        section_name: Nombre de la sección (para estilo dinámico)
    """
    if style_name == "by_section" and section_name:
        style = TitleStyles.style_by_section(section_name)
    else:
        style_method = getattr(TitleStyles, f"style_{style_name}", TitleStyles.style_default)
        style = style_method()
    
    label.configure(**style)

