import customtkinter as ctk
import calendar
from datetime import datetime


class CTkDatePicker(ctk.CTkFrame):
    """
    DatePicker moderno para CustomTkinter.
    Compatible con temas oscuros y sin dependencias externas.
    """

    def __init__(self, master, width=120, **kwargs):
        super().__init__(master, fg_color="transparent")

        self.width = width
        self.selected_date = datetime.now()

        # Campo de texto (readonly)
        self.entry = ctk.CTkEntry(
            self,
            width=self.width,
            corner_radius=6
        )
        self.entry.pack(fill="x")
        self.entry.bind("<Button-1>", self._open_calendar)

        # Inicializar texto
        self._update_entry()

        # Popover (se crea dinámicamente)
        self.calendar_popup = None

    # ------------------------------------------------------------------
    # Entry → abre calendario
    # ------------------------------------------------------------------
    def _open_calendar(self, event=None):
        if self.calendar_popup and self.calendar_popup.winfo_exists():
            self.calendar_popup.destroy()

        self.calendar_popup = ctk.CTkToplevel(self)
        self.calendar_popup.overrideredirect(True)
        self.calendar_popup.configure(fg_color="#1e1e1e")

        # Posición del popover
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        self.calendar_popup.geometry(f"240x240+{x}+{y}")

        self._build_calendar_ui()

    # ------------------------------------------------------------------
    # Construcción del popup de calendario
    # ------------------------------------------------------------------
    def _build_calendar_ui(self):
        self.popup_frame = ctk.CTkFrame(self.calendar_popup, fg_color="#1e1e1e")
        self.popup_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # ---- Barra superior (mes / año) ----
        top = ctk.CTkFrame(self.popup_frame, fg_color="transparent")
        top.pack(fill="x", pady=5)

        ctk.CTkButton(
            top, text="<", width=30, command=self._prev_month,
            fg_color="#333", hover_color="#555"
        ).pack(side="left")

        self.month_label = ctk.CTkLabel(
            top,
            text=self.selected_date.strftime("%B %Y"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.month_label.pack(side="left", expand=True)

        ctk.CTkButton(
            top, text=">", width=30, command=self._next_month,
            fg_color="#333", hover_color="#555"
        ).pack(side="right")

        # ---- Días de la semana ----
        week_days = ["L", "M", "X", "J", "V", "S", "D"]
        row = ctk.CTkFrame(self.popup_frame, fg_color="transparent")
        row.pack(fill="x")

        for d in week_days:
            ctk.CTkLabel(
                row, text=d, width=30,
                fg_color="transparent"
            ).pack(side="left")

        # ---- Calendario de días ----
        self.days_frame = ctk.CTkFrame(self.popup_frame, fg_color="transparent")
        self.days_frame.pack(fill="both", expand=True)

        self._draw_days()

    # ------------------------------------------------------------------
    # Dibujar los días del mes actual
    # ------------------------------------------------------------------
    def _draw_days(self):
        for widget in self.days_frame.winfo_children():
            widget.destroy()

        year = self.selected_date.year
        month = self.selected_date.month
        month_calendar = calendar.monthcalendar(year, month)

        for week in month_calendar:
            row = ctk.CTkFrame(self.days_frame, fg_color="transparent")
            row.pack(fill="x")

            for day in week:
                if day == 0:
                    ctk.CTkLabel(row, text="", width=30).pack(side="left")
                else:
                    btn = ctk.CTkButton(
                        row,
                        text=str(day),
                        width=30,
                        fg_color="#333",
                        hover_color="#444",
                        command=lambda d=day: self._select_day(d)
                    )
                    btn.pack(side="left", padx=1, pady=1)

    # ------------------------------------------------------------------
    # Lógica de selección
    # ------------------------------------------------------------------
    def _select_day(self, day):
        self.selected_date = self.selected_date.replace(day=day)
        self._update_entry()
        self.calendar_popup.destroy()

    # ------------------------------------------------------------------
    # Navegación de meses
    # ------------------------------------------------------------------
    def _prev_month(self):
        year = self.selected_date.year
        month = self.selected_date.month - 1
        if month < 1:
            month = 12
            year -= 1
        self.selected_date = self.selected_date.replace(year=year, month=month)
        self._update_month_view()

    def _next_month(self):
        year = self.selected_date.year
        month = self.selected_date.month + 1
        if month > 12:
            month = 1
            year += 1
        self.selected_date = self.selected_date.replace(year=year, month=month)
        self._update_month_view()

    def _update_month_view(self):
        self.month_label.configure(text=self.selected_date.strftime("%B %Y"))
        self._draw_days()

    # ------------------------------------------------------------------
    # Actualizar campo de texto
    # ------------------------------------------------------------------
    def _update_entry(self):
        # Permite escritura temporalmente
        self.entry.configure(state="normal")

        # Actualiza el texto visible
        self.entry.delete(0, "end")
        self.entry.insert(0, self.get())

        # Bloquea edición manual si NO quieres permitir escribir
        self.entry.configure(state="readonly")


    # ------------------------------------------------------------------
    # Obtener fecha seleccionada en formato yyyy-mm-dd
    # ------------------------------------------------------------------
    def get(self):
        return self.selected_date.strftime("%Y-%m-%d")
