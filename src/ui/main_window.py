import customtkinter as ctk
from PIL import Image
import os
from tkinter import messagebox
from src.ui.dashboard import DashboardWindow
from src.ui.entities.clientes_window import ClientesWindow
from src.ui.entities.empleados_window import EmpleadosWindow
from src.ui.entities.productos_window import ProductosWindow
from src.ui.entities.presupuestos_window import PresupuestosWindow
from src.ui.entities.facturas_window import FacturasWindow
from src.ui.entities.pagos_window import PagosWindow
from src.ui.reports_window import ReportsWindow
from src.ui.help_window import HelpWindow

class MainWindow:

    def __init__(self, root, api, user_info):
        self.root = root
        self.api = api

        # user_info puede venir como None si no hay backend
        self.user_info = user_info or {}

        # Rol seguro
        self.role = (self.user_info.get("rol") or "CLIENTE").upper()

        self.is_admin = self.role == "ADMIN"
        self.is_empleado = self.role == "EMPLEADO"
        self.is_cliente = self.role == "CLIENTE"

        # Username seguro
        self.username = (
            self.user_info.get("nombre")
            or self.user_info.get("username")
            or self.user_info.get("email")
            or f"ID-{self.user_info.get('id', '?')}"
        )

        self.current_frame = None

    # ---------------------------------------------------------
    # Limpieza total entre logins
    # ---------------------------------------------------------
    def destroy_main_content(self):

        if hasattr(self, "content_area"):
            self.content_area.destroy()
            del self.content_area

        if hasattr(self, "topbar"):
            self.topbar.destroy()
            del self.topbar

        if hasattr(self, "statusbar"):
            self.statusbar.destroy()
            del self.statusbar

        if hasattr(self, "main_container"):
            self.main_container.destroy()
            del self.main_container


    # ---------------------------------------------------------
    def show(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root.deiconify()
        self.root.title(f"CRM XTART - {self.username}")
        self.root.geometry("1200x800")
        # self.root.configure(bg_color="#23243a")

        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 600
        y = (self.root.winfo_screenheight() // 2) - 400
        self.root.geometry(f"1200x800+{x}+{y}")
        self.root.bind("<F1>", lambda e: HelpWindow(self.root).show())

        # ---------------------------------------------------------
        # Atajos de teclado (Dashboard y Logout)
        # ---------------------------------------------------------
        self.root.bind("<Control-d>", lambda e: self.show_dashboard())
        self.root.bind("<Control-D>", lambda e: self.show_dashboard())
        self.root.bind("<Control-q>", lambda e: self._logout())
        self.root.bind("<Control-Q>", lambda e: self._logout())
        
        # ---------------------------------------------------------
        # Crear contenedor raíz (SIEMPRE NUEVO)
        # ---------------------------------------------------------

        if hasattr(self, "main_container"):
            self.main_container.destroy()

        self.main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        # UI
        self._create_topbar()
        self._create_statusbar()
        self.show_dashboard()


    # ---------------------------------------------------------
    def _create_topbar(self):
        self.topbar = ctk.CTkFrame(self.main_container, fg_color="#23243a", corner_radius=0)
        self.topbar.pack(side="top", fill="x")

        card = ctk.CTkFrame(
            self.topbar,
            fg_color="white",
            border_width=1,
            border_color="#ccd3db",
            corner_radius=16,
        )
        card.pack(side="left", padx=10, pady=6)

        ctk.CTkLabel(
            card,
            text=f"Bienvenido: {self.username}",
            font=ctk.CTkFont("Arial", 12, "bold"),
            text_color="#293553",
        ).pack(padx=16, pady=8)

        img_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "Images",
            "XtartLogo.png"
        )
        logo_img = Image.open(img_path).resize((60, 60), Image.LANCZOS)
        menu_icon = ctk.CTkImage(
            light_image=logo_img,
            dark_image=logo_img,
            size=(60, 60)
        )

        menu_btn = ctk.CTkButton(
            self.topbar,
            image=menu_icon,
            text="",
            width=60,
            height=60,
            fg_color="#23243a",
            hover_color="#36455e",
            corner_radius=18,
            command=self._toggle_menu,
        )
        menu_btn.image = menu_icon
        menu_btn.pack(side="right", padx=16, pady=6)


    # ---------------------------------------------------------
    def _toggle_menu(self):

        if hasattr(self, "menu_popover_window") and self.menu_popover_window.winfo_exists():
            self.menu_popover_window.destroy()
            return

        options = [("Dashboard", self.show_dashboard)]

        if self.is_admin or self.is_empleado:
            options.append(("Clientes", self.show_clientes))
            if self.is_admin:
                options.append(("Empleados", self.show_empleados))
            options.extend([
                ("Productos", self.show_productos),
                ("Presupuestos", self.show_presupuestos),
                ("Facturas", self.show_facturas),
                ("Pagos", self.show_pagos),
                ("Informes", self.show_reports),
            ])
        else:
            options.extend([
                ("Mi Perfil", self.show_my_profile),
                ("Mis Facturas", self.show_my_facturas),
                ("Mis Pagos", self.show_my_pagos),
            ])

        options.append(("Ayuda", self.show_help))
        options.append(("Salir", self._logout))

        btn_height = 44
        window_width = 150
        window_height = btn_height * len(options) + 20

        x_root = self.root.winfo_rootx()
        y_root = self.root.winfo_rooty()
        w_root = self.root.winfo_width()
        screen_height = self.root.winfo_screenheight()

        pos_x = x_root + w_root - window_width - 70
        if pos_x < 10:
            pos_x = 10

        pos_y = y_root + 110
        max_bottom = screen_height - 40
        if pos_y + window_height > max_bottom:
            pos_y = max_bottom - window_height

        self.menu_popover_window = ctk.CTkToplevel(self.root)
        self.menu_popover_window.overrideredirect(True)
        self.menu_popover_window.geometry(
            f"{window_width}x{window_height}+{pos_x}+{pos_y}"
        )
        self.menu_popover_window.configure(bg="#23243a")

        frame = ctk.CTkFrame(
            self.menu_popover_window,
            fg_color="#23243a",
            corner_radius=12
        )
        frame.pack(fill="both", expand=True)

        for text, command in options:
            btn = ctk.CTkButton(
                frame,
                text=text,
                font=ctk.CTkFont("Arial", 11),
                fg_color="#2491ed",
                hover_color="#137bd6",
                text_color="white",
                corner_radius=10,
                anchor="w",
                width=window_width - 10,
                command=lambda cmd=command: (
                    self.menu_popover_window.destroy(), cmd()
                ),
            )
            btn.pack(fill="x", padx=8, pady=4)

        self.menu_popover_window.focus_force()


    # ---------------------------------------------------------
    def _create_statusbar(self):
        self.statusbar = ctk.CTkLabel(
            self.main_container,
            text="Listo",
            anchor="w",
            fg_color="#23243a",
            text_color="#fff"
        )
        self.statusbar.pack(side="bottom", fill="x")


    # ---------------------------------------------------------
    def _set_status(self, msg):
        self.statusbar.configure(text=msg)


    # ---------------------------------------------------------
    def _clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None


    # ---------------------------------------------------------
    def _ensure_content_area(self):
        if not hasattr(self, "content_area"):
            self.content_area = ctk.CTkFrame(
                self.main_container,
                fg_color="transparent"
            )
            self.content_area.pack(fill="both", expand=True)


    # ---------------------------------------------------------
    def show_dashboard(self):
        self._ensure_content_area()
        self._clear_frame()

        self.current_frame = DashboardWindow(self.content_area, self.api)
        self.current_frame.pack(fill="both", expand=True)

        self._set_status("Dashboard")


    # ---------------------------------------------------------
    def _load_window(self, cls, label):
        self._ensure_content_area()
        self._clear_frame()

        self.current_frame = cls(self.content_area, self.api)
        self.current_frame.pack(fill="both", expand=True)

        self._set_status(label)


    # ---------------------------------------------------------
    # Ventanas CRUD
    # ---------------------------------------------------------
    def show_clientes(self):
        if not (self.is_admin or self.is_empleado):
            return self._no_access()
        self._load_window(ClientesWindow, "Clientes")

    def show_empleados(self):
        if not self.is_admin:
            return self._no_access()
        self._load_window(EmpleadosWindow, "Empleados")

    def show_productos(self):
        if not (self.is_admin or self.is_empleado):
            return self._no_access()
        self._load_window(ProductosWindow, "Productos")

    def show_presupuestos(self):
        if not (self.is_admin or self.is_empleado):
            return self._no_access()
        self._load_window(PresupuestosWindow, "Presupuestos")

    def show_facturas(self):
        if not (self.is_admin or self.is_empleado):
            return self._no_access()
        self._load_window(FacturasWindow, "Facturas")

    def show_pagos(self):
        if not (self.is_admin or self.is_empleado):
            return self._no_access()
        self._load_window(PagosWindow, "Pagos")

    # ---------------------------------------------------------
    # Cliente simple
    # ---------------------------------------------------------
    def show_my_profile(self):
        if not self.is_cliente:
            return self._no_access()
        self._load_window(lambda p, a: ClientesWindow(p, a, client_mode=True), "Mi Perfil")

    def show_my_facturas(self):
        if not self.is_cliente:
            return self._no_access()
        self._load_window(lambda p, a: FacturasWindow(p, a, client_mode=True), "Mis Facturas")

    def show_my_pagos(self):
        if not self.is_cliente:
            return self._no_access()
        self._load_window(lambda p, a: PagosWindow(p, a, client_mode=True), "Mis Pagos")


    # ---------------------------------------------------------
    def show_reports(self):
        if not (self.is_admin or self.is_empleado):
            return self._no_access()
        self._load_window(ReportsWindow, "Informes")


    # ---------------------------------------------------------
    def show_help(self):
        HelpWindow(self.root).show()


    # ---------------------------------------------------------
    def _logout(self):
        if not messagebox.askyesno("Confirmar", "¿Cerrar sesión?"):
            return

        self.api.logout()
        self.destroy_main_content()

        from src.ui.login_window import LoginWindow
        LoginWindow(self.root, self.api).show()


    # ---------------------------------------------------------
    def _no_access(self):
        messagebox.showwarning("Acceso denegado", "No tiene permisos.")
