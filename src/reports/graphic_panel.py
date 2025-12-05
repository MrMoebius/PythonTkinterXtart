from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class GraphicPanel:

    current_canvas = None

    @staticmethod
    def display(parent, figure):
        """
        Renderiza una figura de Matplotlib dentro de un contenedor CTkScrollableFrame o ttk.Frame.
        Reemplaza cualquier gráfico anterior.
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[GRAPHIC_PANEL] Displaying figure in parent: {parent}")
        
        # Limpiar contenido previo
        children_before = len(parent.winfo_children())
        for w in parent.winfo_children():
            w.destroy()
        logger.info(f"[GRAPHIC_PANEL] Limpiados {children_before} widgets anteriores")

        # Crear canvas
        try:
            canvas = FigureCanvasTkAgg(figure, master=parent)
            canvas.draw()
            logger.info(f"[GRAPHIC_PANEL] Canvas creado y dibujado")

            # Obtener widget TK
            widget = canvas.get_tk_widget()
            widget.pack(fill="x", expand=False, pady=10)
            logger.info(f"[GRAPHIC_PANEL] Widget empaquetado en parent")

            # Guardar referencia del canvas actual
            GraphicPanel.current_canvas = canvas

            return canvas
        except Exception as e:
            logger.error(f"[GRAPHIC_PANEL] Error al mostrar gráfico: {e}", exc_info=True)
            raise
