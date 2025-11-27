import customtkinter as ctk
from src.ui.main_window import MainWindow
from tkinter import messagebox

class LoginWindow:
    def __init__(self, root, api_client):
        self.root = root
        self.api = api_client
        self.window = None

    def show(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.window = ctk.CTkToplevel(self.root)
        self.window.title("CRM XTART - Inicio de Sesión")
        self.window.resizable(False, False)

        w, h = 420, 320
        self.window.geometry(f"{w}x{h}")
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - w) // 2
        y = (self.window.winfo_screenheight() - h) // 2
        self.window.geometry(f"{w}x{h}+{x}+{y}")

        self._create_widgets()
        self.window.bind("<Return>", lambda e: self._login())

    def _create_widgets(self):
        import os
        from PIL import Image

        panel = ctk.CTkFrame(self.window, corner_radius=12)
        panel.pack(expand=True, fill="both", padx=28, pady=24)

        img_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "Images",
            "XtartLogo.png"
        )
        logo_img = Image.open(img_path).resize((80, 80), Image.LANCZOS)
        logo_icon = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(80, 80))

        ctk.CTkLabel(panel, image=logo_icon, text="").pack(pady=(5, 8))

        ctk.CTkLabel(panel, text="CRM XTART", font=ctk.CTkFont(size=25, weight="bold")).pack(pady=(0, 16))

        self.username_entry = ctk.CTkEntry(panel, placeholder_text="Usuario", width=240)
        self.username_entry.pack(pady=(6, 10))
        self.username_entry.focus()

        self.password_entry = ctk.CTkEntry(panel, placeholder_text="Contraseña", width=240, show="*")
        self.password_entry.pack(pady=(2, 20))

        ctk.CTkButton(panel, text="Iniciar Sesión", width=190, command=self._login).pack(pady=3)

        ctk.CTkLabel(
            panel,
            text="Ingrese sus credenciales para acceder al sistema",
            font=ctk.CTkFont(size=10),
            text_color="#aaa"
        ).pack(pady=7)

    def _login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Por favor, complete todos los campos")
            return

        # Indicador de espera
        self.window.config(cursor="wait")
        self.window.update()

        result = self.api.login(username, password)

        # Restaurar cursor
        self.window.config(cursor="")

        # -------------------------
        # SI BACKEND NO RESPONDE
        # -------------------------
        # if not result.get("success"):
        #     messagebox.showerror("Error", result.get("error", "Backend no disponible"))

        #     # MODO VISUAL COMO ADMIN
        #     fake_user = {
        #         "rol": "ADMIN",
        #         "nombre": "Administrador (modo visual)",
        #         "username": "admin",
        #         "email": "admin@local"
        #     }

        #     self.window.destroy()
        #     self.root.deiconify()

        #     from src.ui.main_window import MainWindow
        #     main_window = MainWindow(self.root, self.api, fake_user)
        #     main_window.show()
        #     return

        # -------------------------
        # LOGIN CORRECTO
        # -------------------------
        user_info = result["data"]

        self.window.destroy()
        self.root.deiconify()

        # Selección de dashboard según tipo/rol
        tipo = user_info.get("tipo", "").lower()
        rol = user_info.get("rol", "").lower()

        if tipo == "cliente":
            from src.ui.client_dashboard import ClientDashboard
            dashboard = ClientDashboard(self.root, self.api, user_info)

        elif tipo == "empleado" and rol == "admin":
            from src.ui.admin_dashboard import AdminDashboard
            dashboard = AdminDashboard(self.root, self.api, user_info)

        else:
            from src.ui.employee_dashboard import EmployeeDashboard
            dashboard = EmployeeDashboard(self.root, self.api, user_info)

        dashboard.show()

