class ImageExporter:

    @staticmethod
    def export(figure, path):
        # Exportar PNG con buena resolución manteniendo proporción A4
        figure.savefig(path, format="png", dpi=150, bbox_inches="tight")
