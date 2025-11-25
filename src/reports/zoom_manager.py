class ZoomManager:

    def __init__(self):
        self.scale = 1.0

    def zoom_in(self):
        self.scale += 0.1

    def zoom_out(self):
        self.scale = max(0.2, self.scale - 0.1)

    def apply_zoom(self, widget):
        widget.scale("all", 0, 0, self.scale, self.scale)
