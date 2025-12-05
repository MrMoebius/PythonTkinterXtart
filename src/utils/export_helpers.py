"""
Funciones auxiliares comunes para exportación de documentos (PDF/PNG).
Usado por presupuestos, facturas y pagos.
"""

import os
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


class DocumentExporter:
    """Clase helper para crear documentos con formato común (tarjetas, logo, etc.)"""
    
    def __init__(self, fig: Figure, ax):
        """
        Args:
            fig: Figura de matplotlib
            ax: Eje de matplotlib
        """
        self.fig = fig
        self.ax = ax
        self.y_position = 0.965
        self.line_height = 0.027
        self.KEY_X = 0.11
        self.VAL_X = 0.34
        
        # Configurar eje
        ax.axis('off')
    
    def add_logo(self, logo_path: str = "src/Images/XtartLogo.png", position: str = "top_right"):
        """
        Añade el logo en un eje independiente para evitar distorsión.
        position: "top_left" o "top_right"
        """
        import matplotlib.image as mpimg

        if not os.path.exists(logo_path):
            return

        logo = mpimg.imread(logo_path)

        # Tamaño del logo: porcentaje del ancho/alto de la figura
        logo_width = 0.10     # 10% del ancho del A4
        logo_height = 0.10    # 10% del alto del A4

        # Posiciones absolutas en la FIGURA (no en el eje principal)
        if position == "top_right":
            x0 = 0.88   # 88% -> esquina derecha
            y0 = 0.83   # 83% -> arriba
        else:
            x0 = 0.02
            y0 = 0.83

        # Crear un eje nuevo exclusivo para el logo
        ax_logo = self.fig.add_axes([x0, y0, logo_width, logo_height])
        ax_logo.imshow(logo)
        ax_logo.axis("off")

    
    def add_main_title(self, title: str, subtitle: str = None):
        """Añade título principal y subtítulo centrados."""
        self.ax.text(0.50, 0.983, title, ha="center", fontsize=22, weight='bold', transform=self.ax.transAxes)
        if subtitle:
            self.ax.text(0.50, 0.958, subtitle, ha="center", fontsize=13, transform=self.ax.transAxes)
        self.y_position = 0.92
    
    def add_row(self, key: str, value, fontsize: int = 11):
        """Línea clave–valor alineada + separador interno."""
        self.ax.text(self.KEY_X, self.y_position, f"{key}:", fontsize=fontsize, weight='bold', transform=self.ax.transAxes)
        self.ax.text(self.VAL_X, self.y_position, str(value), fontsize=fontsize, transform=self.ax.transAxes)
        
        self.y_position -= self.line_height * 0.80
        self.ax.axhline(self.y_position + 0.009, xmin=self.KEY_X, xmax=0.88, color="#aaaaaa", linewidth=0.55)
        self.y_position -= self.line_height * 0.35
    
    def add_title(self, text: str, fontsize: int = 13):
        """Título de sección alineado a la izquierda dentro de tarjeta."""
        self.ax.text(0.10, self.y_position, text, fontsize=fontsize, weight='bold', transform=self.ax.transAxes)
        self.y_position -= self.line_height
    
    def separator(self):
        """Línea horizontal entre tarjetas."""
        self.ax.axhline(self.y_position + 0.006, xmin=0.075, xmax=0.93, color='black', linewidth=0.9)
    
    def draw_card(self, y_top: float, y_bottom: float):
        """Tarjeta doble borde estilo moderno."""
        rect_outer = plt.Rectangle((0.08, y_bottom), 0.84, y_top - y_bottom,
                                fill=False, linewidth=1.7, transform=self.ax.transAxes)
        rect_inner = plt.Rectangle((0.082, y_bottom + 0.003), 0.836, (y_top - y_bottom) - 0.006,
                                fill=False, linewidth=0.8, transform=self.ax.transAxes)
        self.ax.add_patch(rect_outer)
        self.ax.add_patch(rect_inner)
    
    def create_section(self, title: str, items: list, include_card: bool = True):
        """
        Crea una sección completa con título, filas y tarjeta.
        
        Args:
            title: Título de la sección
            items: Lista de tuplas (key, value) para mostrar
            include_card: Si True, dibuja la tarjeta alrededor
        
        Returns:
            (y_top, y_bottom) para usar con draw_card si include_card=False
        """
        self.separator()
        top = self.y_position
        
        self.add_title(title)
        for key, value in items:
            self.add_row(key, value)
        
        bottom = self.y_position - 0.008
        if include_card:
            self.draw_card(top, bottom)
        
        self.y_position = bottom - 0.028
        return (top, bottom)


def create_document_base() -> tuple:
    """
    Crea la base del documento (figura y eje) en formato A4 horizontal.
    
    Returns:
        (fig, ax) - Figura y eje de matplotlib
    """
    # A4 horizontal en pulgadas: 11.69 x 8.27 (ancho x alto)
    fig = Figure(figsize=(11.69, 8.27), dpi=120)
    ax = fig.add_subplot(111)
    return fig, ax

