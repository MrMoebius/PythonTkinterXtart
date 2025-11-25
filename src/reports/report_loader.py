import random
from datetime import datetime, timedelta


class ReportLoader:
    """
    Carga datos para informes.
    MODO AUTOMÁTICO:
    - Si api es DemoClient → usa datos simulados
    - Si api es RestClient  → consulta servidor Jakarta
    """

    def __init__(self, api):
        self.api = api
        self.is_demo = api.__class__.__name__.lower().startswith("demo")

    # ================================================================
    # HELPER → FORMATO DE RESPUESTA
    # ================================================================
    def _success(self, data):
        return data if data else None

    # ================================================================
    # INFORME 1 → Ventas por empleado
    # ================================================================
    def ventas_por_empleado(self, desde=None, hasta=None):
        # Modo demo
        if self.is_demo:
            return self._demo_ventas_por_empleado()
        # Construir parámetros
        params = {}
        if desde:
            params["desde"] = desde
        if hasta:
            params["hasta"] = hasta
        # Petición API con fechas
        res = self.api.get("/informes/ventas-empleado", params=params)
        if not res or not res.get("success"):
            return None
        return res.get("data")

    # ================================================================
    # INFORME 2 → Estado presupuestos
    # ================================================================
    def estados_presupuestos(self, desde=None, hasta=None):
        # Modo demo
        if self.is_demo:
            return self._demo_estado_presupuestos()
        # Construir parámetros
        params = {}
        if desde:
            params["desde"] = desde
        if hasta:
            params["hasta"] = hasta
        # Petición API con fechas
        res = self.api.get("/informes/presupuestos-estado", params=params)
        if not res or not res.get("success"):
            return None
        return res.get("data")

    # ================================================================
    # INFORME 3 → Facturación mensual
    # ================================================================
    def facturacion_mensual(self, desde=None, hasta=None):
        if self.is_demo:
            return self._demo_facturacion_mensual()
        # Construir parámetros
        params = {}
        if desde:
            params["desde"] = desde
        if hasta:
            params["hasta"] = hasta
        # Petición API con fechas
        res = self.api.get("/informes/facturacion-mensual", params=params)
        if not res or not res.get("success"):
            return None
        return res.get("data")

    # ================================================================
    # INFORME 4 → Ventas por producto
    # ================================================================
    def ventas_por_producto(self, desde=None, hasta=None):
        if self.is_demo:
            return self._demo_ventas_por_producto()
        # Construir parámetros
        params = {}
        if desde:
            params["desde"] = desde
        if hasta:
            params["hasta"] = hasta
        # Petición API con fechas
        res = self.api.get("/informes/ventas-producto", params=params)
        if not res or not res.get("success"):
            return None
        return res.get("data")

    # ================================================================
    # INFORME 5 → Ratio de conversión
    # ================================================================
    def ratio_conversion(self, desde=None, hasta=None):
        if self.is_demo:
            return self._demo_ratio_conversion()
        # Construir parámetros
        params = {}
        if desde:
            params["desde"] = desde
        if hasta:
            params["hasta"] = hasta
        # Petición API con fechas
        res = self.api.get("/informes/ratio-conversion", params=params)
        if not res or not res.get("success"):
            return None
        return res.get("data")

    # ===================================================================
    # ===================================================================
    #                           MODO DEMO
    # ===================================================================
    # ===================================================================

    # ---------------------------------------------------------
    # DEMO → Ventas por empleado
    # ---------------------------------------------------------
    def _demo_ventas_por_empleado(self):
        fake = [
            {"nombre": "Juan Pérez", "total": 15200},
            {"nombre": "Ana Gómez", "total": 9800},
            {"nombre": "Carlos Ruiz", "total": 7200},
            {"nombre": "Lucía Martín", "total": 18400},
        ]
        return self._success(fake)

    # ---------------------------------------------------------
    # DEMO → Estado presupuestos
    # ---------------------------------------------------------
    def _demo_estado_presupuestos(self):
        fake = {
            "Aceptado": 12,
            "Pendiente": 18,
            "Rechazado": 5,
            "Caducado": 3
        }
        return self._success(fake)

    # ---------------------------------------------------------
    # DEMO → Facturación mensual
    # ---------------------------------------------------------
    def _demo_facturacion_mensual(self):
        base_date = datetime.now().replace(day=1)
        fake = {}

        for i in range(12):
            month = (base_date - timedelta(days=30 * i)).strftime("%Y-%m")
            fake[month] = random.randint(3000, 20000)

        return self._success(fake)

    # ---------------------------------------------------------
    # DEMO → Ventas por producto
    # ---------------------------------------------------------
    def _demo_ventas_por_producto(self):
        fake = [
            {"producto": "Curso Python", "total": 12000},
            {"producto": "Curso Java", "total": 9500},
            {"producto": "Curso Ciberseguridad", "total": 7600},
            {"producto": "Curso Kotlin", "total": 6400},
        ]
        return self._success(fake)

    # ---------------------------------------------------------
    # DEMO → Ratio conversión
    # ---------------------------------------------------------
    def _demo_ratio_conversion(self):
        fake = {
            "Convertidos": 48,
            "No interesados": 28,
            "Pendientes": 15,
            "Contactados": 9
        }
        return self._success(fake)
