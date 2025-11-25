from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class GraphicPanel:

    current_canvas = None

    @staticmethod
    def display(parent, figure):
        """
        Renderiza una figura de Matplotlib dentro de un contenedor CTkScrollableFrame o ttk.Frame.
        Reemplaza cualquier gráfico anterior.
        """
        # Limpiar contenido previo
        for w in parent.winfo_children():
            w.destroy()

        # Crear canvas
        canvas = FigureCanvasTkAgg(figure, master=parent)
        canvas.draw()

        # Obtener widget TK
        widget = canvas.get_tk_widget()
        widget.pack(fill="both", expand=True)

        # Guardar referencia del canvas actual
        GraphicPanel.current_canvas = canvas

        return canvas
