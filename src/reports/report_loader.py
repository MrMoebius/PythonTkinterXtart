class ReportLoader:
    """Carga datos de informes desde el backend."""

    def __init__(self, api):
        self.api = api

    # ================================================================
    # INFORME 1 → Ventas por empleado
    # ================================================================
    def ventas_por_empleado(self, desde=None, hasta=None):
        # Construir parámetros
        params = {}
        if desde:
            params["desde"] = desde
        if hasta:
            params["hasta"] = hasta
        # Petición API con fechas
        res = self.api.get("/informes/ventas-empleado", params=params)
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"[REPORT_LOADER] Parámetros enviados: desde={desde}, hasta={hasta}")
        logger.info(f"[REPORT_LOADER] Respuesta completa: {res}")
        
        if not res or not res.get("success"):
            error = res.get("error", "") if res else ""
            logger.error(f"Error al obtener ventas por empleado: {error}")
            return []
        
        data = res.get("data")
        logger.info(f"[REPORT_LOADER] Data extraída: {data} (type: {type(data)})")
        
        if data is None:
            logger.warning("[REPORT_LOADER] Data es None, devolviendo lista vacía")
            return []
        
        if isinstance(data, list):
            logger.info(f"[REPORT_LOADER] Datos recibidos: {len(data)} elementos")
            if len(data) > 0:
                logger.info(f"[REPORT_LOADER] Primer elemento: {data[0]}")
        else:
            logger.warning(f"[REPORT_LOADER] Data no es una lista, es: {type(data)}")
        
        return data

    # ================================================================
    # INFORME 2 → Estado presupuestos
    # ================================================================
    def estados_presupuestos(self, desde=None, hasta=None):
        # Construir parámetros
        params = {}
        if desde:
            params["desde"] = desde
        if hasta:
            params["hasta"] = hasta
        # Petición API con fechas
        res = self.api.get("/informes/presupuestos-estado", params=params)
        import logging
        logger = logging.getLogger(__name__)
        
        if not res or not res.get("success"):
            error = res.get("error", "") if res else ""
            logger.error(f"Error al obtener estado presupuestos: {error}")
            return {}
        
        data = res.get("data")
        if data is None:
            return {}
        
        # Si el backend devuelve una lista vacía en lugar de un diccionario, convertir
        if isinstance(data, list):
            logger.warning("[REPORT_LOADER] Backend devolvió lista vacía, esperado diccionario. Convirtiendo a {}")
            return {}
        
        logger.info(f"[REPORT_LOADER] Datos recibidos: {data}")
        return data

    # ================================================================
    # INFORME 3 → Facturación mensual
    # ================================================================
    def facturacion_mensual(self, desde=None, hasta=None):
        # Construir parámetros
        params = {}
        if desde:
            params["desde"] = desde
        if hasta:
            params["hasta"] = hasta
        # Petición API con fechas
        res = self.api.get("/informes/facturacion-mensual", params=params)
        import logging
        logger = logging.getLogger(__name__)
        
        if not res or not res.get("success"):
            error = res.get("error", "") if res else ""
            logger.error(f"Error al obtener facturación mensual: {error}")
            return {}
        
        data = res.get("data")
        if data is None:
            return {}
        
        # Si el backend devuelve una lista vacía en lugar de un diccionario, convertir
        if isinstance(data, list):
            logger.warning("[REPORT_LOADER] Backend devolvió lista vacía, esperado diccionario. Convirtiendo a {}")
            return {}
        
        logger.info(f"[REPORT_LOADER] Datos recibidos: {len(data)} meses")
        return data

    # ================================================================
    # INFORME 4 → Ventas por producto
    # ================================================================
    def ventas_por_producto(self, desde=None, hasta=None):
        # Construir parámetros
        params = {}
        if desde:
            params["desde"] = desde
        if hasta:
            params["hasta"] = hasta
        # Petición API con fechas
        res = self.api.get("/informes/ventas-producto", params=params)
        import logging
        logger = logging.getLogger(__name__)
        
        if not res or not res.get("success"):
            error = res.get("error", "") if res else ""
            logger.error(f"Error al obtener ventas por producto: {error}")
            return []
        
        data = res.get("data")
        if data is None:
            return []
        
        logger.info(f"[REPORT_LOADER] Datos recibidos: {len(data) if isinstance(data, list) else 'dict'} elementos")
        return data

    # ================================================================
    # INFORME 5 → Ratio de conversión
    # ================================================================
    def ratio_conversion(self, desde=None, hasta=None):
        # Construir parámetros
        params = {}
        if desde:
            params["desde"] = desde
        if hasta:
            params["hasta"] = hasta
        # Petición API con fechas
        res = self.api.get("/informes/ratio-conversion", params=params)
        import logging
        logger = logging.getLogger(__name__)
        
        if not res or not res.get("success"):
            error = res.get("error", "") if res else ""
            logger.error(f"Error al obtener ratio conversión: {error}")
            return {}
        
        data = res.get("data")
        if data is None:
            return {}
        
        # Si el backend devuelve una lista vacía en lugar de un diccionario, convertir
        if isinstance(data, list):
            logger.warning("[REPORT_LOADER] Backend devolvió lista vacía, esperado diccionario. Convirtiendo a {}")
            return {}
        
        logger.info(f"[REPORT_LOADER] Datos recibidos: {data}")
        return data

