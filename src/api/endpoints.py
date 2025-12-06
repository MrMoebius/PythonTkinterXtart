"""
Mapeo de endpoints del backend Java/Jakarta
"""


class Endpoints:
    """Endpoints de la API REST del backend"""
    
    # Base URL - se puede configurar desde settings
    # Backend Java: crudxtart
    BASE_URL = "http://localhost:8080/crudxtart"
    
    # Autenticación
    AUTH_LOGIN = "/login"
    AUTH_LOGOUT = "/logout"
    
    # Clientes
    CLIENTES = "/clientes"
    CLIENTE_BY_ID = "/clientes/{id}"
    
    # Empleados
    EMPLEADOS = "/empleados"
    EMPLEADO_BY_ID = "/empleados/{id}"
    ROLES_EMPLEADO = "/roles_empleado"
    
    # Productos
    PRODUCTOS = "/productos"
    PRODUCTO_BY_ID = "/productos/{id}"
    
    # Facturas
    FACTURAS = "/facturas"
    FACTURA_BY_ID = "/facturas/{id}"
    FACTURA_DETALLES = "/factura_productos"
    FACTURA_DETALLES_BY_FACTURA = "/factura_productos?factura_id={factura_id}"
    
    # Presupuestos
    PRESUPUESTOS = "/presupuestos"
    PRESUPUESTO_BY_ID = "/presupuestos/{id}"
    
    # Pagos
    PAGOS = "/pagos"
    PAGO_BY_ID = "/pagos/{id}"
    
    # Dashboard
    DASHBOARD_STATS = "/dashboard/stats"
    
    @staticmethod
    def build_url(endpoint: str, **kwargs) -> str:
        """Construye una URL completa reemplazando parámetros"""
        url = endpoint
        for key, value in kwargs.items():
            url = url.replace(f"{{{key}}}", str(value))
        return f"{Endpoints.BASE_URL}{url}"

