import customtkinter as ctk
from abc import ABC, abstractmethod


class DashboardBase(ctk.CTkFrame, ABC):
    """Base visual para Dashboard (título, layout, contenedores)
       Las subclases implementan:
       - _load_stats()
       - _build_quick_access(parent)
    """

    def __init__(self, parent, api, navigation_callback=None):
        super().__init__(parent, fg_color="#23243a")
        self.api = api
        self.navigation = navigation_callback

        self._create_widgets()
        self._load_stats()

    # ================================================================
    # Estructura general del dashboard
    # ================================================================
    def _create_widgets(self):
        # Título
        title = ctk.CTkLabel(
            self,
            text="Dashboard",
            font=("Arial", 26, "bold"),
            text_color="white"
        )
        title.pack(pady=14)

        # Frame de estadísticas
        stats_frame = ctk.CTkFrame(self, fg_color="#252932", corner_radius=16)
        stats_frame.pack(fill="x", padx=24, pady=12)

        self.stats_container = ctk.CTkFrame(stats_frame, fg_color="#252932")
        self.stats_container.pack(fill="both", expand=True, pady=6)

        # Quick Access (solo si subclase lo activa)
        if self.show_quick_access:
            quick_frame = ctk.CTkFrame(self, fg_color="#252932", corner_radius=16)
            quick_frame.pack(fill="x", padx=24, pady=10)
            self._build_quick_access(quick_frame)

    # ================================================================
    # Métodos abstractos
    # ================================================================
    @property
    @abstractmethod
    def show_quick_access(self):
        """Indica si este rol tiene accesos rápidos"""
        pass

    @abstractmethod
    def _load_stats(self):
        """Carga estadísticas según rol"""
        pass

    @abstractmethod
    def _build_quick_access(self, parent):
        """Crea los botones de acceso rápido"""
        pass
