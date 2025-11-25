class PDFExporter:
    @staticmethod
    def export(figure, path):
        figure.savefig(path, format="pdf")
