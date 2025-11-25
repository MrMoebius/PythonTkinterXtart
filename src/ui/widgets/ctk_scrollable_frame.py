import customtkinter as ctk
import tkinter as tk


class CTkScrollableFrame(ctk.CTkFrame):
    """
    ScrollableFrame para CustomTkinter con scroll vertical y horizontal.
    Se comporta como un CTkFrame normal pero con canvas scrolleable.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent")

        # Canvas + Scrollbars
        self.canvas = tk.Canvas(self, highlightthickness=0, bg="#1e1e1e")
        self.v_scroll = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.h_scroll = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)

        self.canvas.configure(yscrollcommand=self.v_scroll.set,
                              xscrollcommand=self.h_scroll.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.v_scroll.pack(side="right", fill="y")
        self.h_scroll.pack(side="bottom", fill="x")

        # Frame interior (contenedor real)
        self.inner_frame = ctk.CTkFrame(self.canvas, fg_color="transparent")

        self.frame_id = self.canvas.create_window(
            (0, 0), window=self.inner_frame, anchor="nw"
        )

        self.inner_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

    # Ajustar scroll region
    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # Expansión horizontal automática
    def _on_canvas_configure(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.frame_id, width=canvas_width)
