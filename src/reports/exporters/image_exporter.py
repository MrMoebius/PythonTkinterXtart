class ImageExporter:

    @staticmethod
    def export(figure, path):
        figure.savefig(path, format="png")
