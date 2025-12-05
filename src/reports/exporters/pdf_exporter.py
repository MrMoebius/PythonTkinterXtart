class PDFExporter:
    @staticmethod
    def export(figure, path):
        # Exportar siempre en formato vectorial PDF con márgenes ajustados
        figure.savefig(path, format="pdf", bbox_inches="tight")
