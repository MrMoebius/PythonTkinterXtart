import json
import os


class DemoClient:
    """
    Cliente DEMO totalmente compatible con RESTClient.
    Maneja login, CRUD, filtros y datos para el dashboard.
    """

    def __init__(self):
        self.base = "demo_data"           # Carpeta donde están los JSON
        self.token = None
        self.user_role = None            # admin | empleado1 | cliente1
        self.user_id = None
        self.username = None

    # --------------------------------------------------
    # LOGIN
    # --------------------------------------------------
    def login(self, username, password=None):
        """
        Login simple por nombre sin contraseña real.
        """
        path = os.path.join(self.base, "login.json")

        if not os.path.exists(path):
            return {"success": False, "error": "Archivo login.json no encontrado"}

        with open(path, "r", encoding="utf-8") as f:
            logins = json.load(f)

        key = username.lower()
        if key not in logins:
            return {"success": False, "error": "Usuario no encontrado"}

        result = logins[key]

        # Simular token/identidad como RESTClient
        self.token = result["token"]
        self.user_role = result["rol"]
        self.user_id = result["id"]
        self.username = result.get("username", username)

        return {"success": True, "data": result}

    def logout(self):
        self.token = None
        self.user_id = None
        self.user_role = None
        self.username = None

    # --------------------------------------------------
    # LOAD / SAVE
    # --------------------------------------------------
    def _load(self, filename):
        """Carga un archivo JSON seguro."""
        path = os.path.join(self.base, filename)

        if not os.path.exists(path):
            return {"success": False, "error": f"{filename} no encontrado"}

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            return {"success": False, "error": f"JSON inválido en {filename}"}

        if not isinstance(data, list):
            data = []

        return {"success": True, "data": data}

    def _save(self, filename, data):
        """Guarda una lista JSON de forma segura."""
        path = os.path.join(self.base, filename)

        with open(path, "w", encoding="utf-8") as f:

            ordered = []
            if filename == "clientes.json":
                order = ["id", "nombre", "apellidos", "email", "telefono", "direccion"]
            else:
                # No reordenar empleados.json ni otros
                json.dump(data, f, indent=2, ensure_ascii=False)
                return


            for item in data:
                fixed = {k: item.get(k) for k in order}
                ordered.append(fixed)

            json.dump(
                ordered,
                f,
                indent=2,
                ensure_ascii=False
            )


    # --------------------------------------------------
    # CRUD GENÉRICO
    # --------------------------------------------------
    def get_all(self, entidad, params=None):
        result = self._load(f"{entidad}.json")
        if not result["success"]:
            return result

        data = result["data"]

        # Si no hay filtros → devolver todo
        if not params:
            return {"success": True, "data": data}

        filtrado = []

        for row in data:
            ok = True
            for k, v in params.items():

                row_val = row.get(k)

                if row_val is None:
                    ok = False
                    break

                # Comparación segura (string o int)
                row_val_str = str(row_val).lower()
                v_str = str(v).lower()

                if v_str not in row_val_str:
                    ok = False
                    break

            if ok:
                filtrado.append(row)

        return {"success": True, "data": filtrado}


    def get_by_id(self, entidad, entity_id):
        result = self._load(f"{entidad}.json")
        if not result["success"]:
            return result

        for item in result["data"]:
            if item.get("id") == entity_id:
                return {"success": True, "data": item}

        return {"success": False, "error": "No encontrado"}

    def create(self, entidad, payload):
        result = self._load(f"{entidad}.json")
        if not result["success"]:
            return result

        data = result["data"]
        new_id = max([i.get("id", 0) for i in data], default=0) + 1

        payload["id"] = new_id
        data.append(payload)
        self._save(f"{entidad}.json", data)

        return {"success": True, "data": payload}

    def update(self, entidad, entity_id, payload):
        result = self._load(f"{entidad}.json")
        if not result["success"]:
            return result

        data = result["data"]

        for i, item in enumerate(data):
            if item.get("id") == entity_id:
                new_item = item.copy()
                new_item.update(payload)
                data[i] = new_item
                self._save(f"{entidad}.json", data)
                return {"success": True, "data": new_item}

        return {"success": False, "error": "No encontrado"}

    def delete(self, entidad, entity_id):
        result = self._load(f"{entidad}.json")
        if not result["success"]:
            return result

        data = [item for item in result["data"] if item.get("id") != entity_id]
        self._save(f"{entidad}.json", data)

        return {"success": True, "data": None}

    # --------------------------------------------------
    # MÉTODOS ESPECÍFICOS USADOS POR LA APP
    # --------------------------------------------------
    def get_roles_empleado(self):
        return self.get_all("roles_empleado")

    def get_empleados(self):
        return self.get_all("empleados")

    def get_clientes(self):
        return self.get_all("clientes")

    def get_cliente_by_id(self, cliente_id):
        return self.get_by_id("clientes", cliente_id)

    def get_productos(self):
        return self.get_all("productos")

    def get_presupuestos(self):
        return self.get_all("presupuestos")

    def get_facturas(self):
        return self.get_all("facturas")

    def get_pagos(self):
        return self.get_all("pagos")

    def get_factura_productos(self, factura_id=None):
        if factura_id:
            return self.get_all("factura_productos",
                                params={"factura_id": factura_id})
        return self.get_all("factura_productos")

    # ------------------------------
    # CLIENTE LOGUEADO
    # ------------------------------
    def get_my_facturas(self):
        return self.get_all("facturas",
                            params={"cliente_id": self.user_id})

    def get_my_pagos(self):
        return self.get_all("pagos",
                            params={"cliente_id": self.user_id})

    # ------------------------------
    # DASHBOARD
    # ------------------------------
    def get_dashboard_stats(self):
        stats = {}

        for entidad in [
            "clientes", "empleados", "productos",
            "presupuestos", "facturas", "pagos"
        ]:
            res = self.get_all(entidad)
            stats[entidad] = len(res["data"]) if res["success"] else 0

        return {"success": True, "data": stats}
