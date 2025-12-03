"""
Módulo helper con métodos específicos del cliente REST.
Contiene métodos de conveniencia para dashboard, clientes, etc.
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class RESTHelpers:
    """Clase helper con métodos específicos del cliente REST."""
    
    def __init__(self, api):
        """
        Args:
            api: Instancia de RESTClient
        """
        self.api = api
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales para admin/empleado.
        Calcula conteos de todas las entidades.
        
        Returns:
            Dict con 'success' y 'data' (diccionario con estadísticas) o 'error'
        """
        try:
            stats = {}
            
            # Obtener conteos de cada entidad
            clientes_res = self.api.get_all("clientes")
            if clientes_res.get("success"):
                clientes_data = clientes_res.get("data", [])
                stats["clientes"] = len(clientes_data) if isinstance(clientes_data, list) else 0
            
            empleados_res = self.api.get_all("empleados")
            if empleados_res.get("success"):
                empleados_data = empleados_res.get("data", [])
                stats["empleados"] = len(empleados_data) if isinstance(empleados_data, list) else 0
            
            productos_res = self.api.get_all("productos")
            if productos_res.get("success"):
                productos_data = productos_res.get("data", [])
                stats["productos"] = len(productos_data) if isinstance(productos_data, list) else 0
            
            try:
                presupuestos_res = self.api.get_all("presupuestos")
                if presupuestos_res.get("success"):
                    presupuestos_data = presupuestos_res.get("data", [])
                    stats["presupuestos"] = len(presupuestos_data) if isinstance(presupuestos_data, list) else 0
            except Exception as e:
                logger.warning(f"Error al cargar presupuestos para estadísticas: {e}")
                stats["presupuestos"] = 0
            
            facturas_res = self.api.get_all("facturas")
            if facturas_res.get("success"):
                facturas_data = facturas_res.get("data", [])
                stats["facturas"] = len(facturas_data) if isinstance(facturas_data, list) else 0
            
            pagos_res = self.api.get_all("pagos")
            if pagos_res.get("success"):
                pagos_data = pagos_res.get("data", [])
                stats["pagos"] = len(pagos_data) if isinstance(pagos_data, list) else 0
            
            return {"success": True, "data": stats}
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {"success": False, "data": {}}
    
    def get_my_facturas(self, cliente_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Obtiene las facturas del cliente actual.
        
        Args:
            cliente_id: ID del cliente (opcional, usa user_id si no se proporciona)
        
        Returns:
            Dict con 'success' y 'data' (lista de facturas) o 'error'
        """
        if cliente_id is None:
            cliente_id = self.api.user_id
        
        if cliente_id is None:
            return {"success": False, "error": "No se pudo identificar el cliente"}
        
        # Obtener todas las facturas y filtrar por cliente
        result = self.api.get_all("facturas")
        if result.get("success") and result.get("data"):
            facturas = result["data"]
            # Asegurar que facturas es una lista
            if not isinstance(facturas, list):
                facturas = []
            
            # Filtrar facturas del cliente
            # El backend Java devuelve facturas con cliente_pagador como objeto o como ID directo
            my_facturas = []
            for factura in facturas:
                if not isinstance(factura, dict):
                    continue
                
                # Intentar obtener el ID del cliente de diferentes formas
                cliente_pagador_id = None
                
                # 1. Desde objeto anidado cliente_pagador
                cliente_pagador = factura.get("cliente_pagador")
                if isinstance(cliente_pagador, dict):
                    cliente_pagador_id = cliente_pagador.get("id_cliente") or cliente_pagador.get("id")
                
                # 2. Desde campo directo id_cliente
                if not cliente_pagador_id:
                    cliente_pagador_id = factura.get("id_cliente")
                
                # 3. Desde campo directo cliente_id
                if not cliente_pagador_id:
                    cliente_pagador_id = factura.get("cliente_id")
                
                # 4. Si cliente_pagador es directamente un ID
                if not cliente_pagador_id and not isinstance(cliente_pagador, dict):
                    cliente_pagador_id = cliente_pagador
                
                # Comparar IDs (convertir a int para comparación segura)
                try:
                    if cliente_pagador_id is not None:
                        cliente_pagador_id_int = int(cliente_pagador_id)
                        cliente_id_int = int(cliente_id)
                        if cliente_pagador_id_int == cliente_id_int:
                            my_facturas.append(factura)
                except (ValueError, TypeError):
                    # Si no se puede convertir, comparar directamente
                    if cliente_pagador_id == cliente_id:
                        my_facturas.append(factura)
            
            logger.info(f"get_my_facturas: cliente_id={cliente_id}, encontradas {len(my_facturas)} facturas")
            return {"success": True, "data": my_facturas}
        
        # Si no hay éxito o no hay data, devolver lista vacía
        return {"success": True, "data": []}
    
    def get_my_pagos(self, cliente_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Obtiene los pagos del cliente actual.
        
        Args:
            cliente_id: ID del cliente (opcional, usa user_id si no se proporciona)
        
        Returns:
            Dict con 'success' y 'data' (lista de pagos) o 'error'
        """
        if cliente_id is None:
            cliente_id = self.api.user_id
        
        if cliente_id is None:
            return {"success": False, "error": "No se pudo identificar el cliente"}
        
        # Obtener todas las facturas del cliente primero
        facturas_res = self.get_my_facturas(cliente_id)
        if not facturas_res.get("success"):
            return {"success": True, "data": []}
        
        facturas = facturas_res.get("data")
        # Asegurar que facturas es una lista
        if facturas is None:
            facturas = []
        elif not isinstance(facturas, list):
            facturas = []
        
        # Obtener IDs de facturas de diferentes formas
        factura_ids = []
        for f in facturas:
            if not isinstance(f, dict):
                continue
            # Intentar obtener ID de diferentes campos
            factura_id = f.get("id_factura") or f.get("id")
            if factura_id:
                factura_ids.append(factura_id)
        
        if not factura_ids:
            logger.info(f"get_my_pagos: cliente_id={cliente_id}, no hay facturas, retornando pagos vacíos")
            return {"success": True, "data": []}
        
        # Obtener todos los pagos y filtrar por facturas del cliente
        pagos_res = self.api.get_all("pagos")
        if pagos_res.get("success") and pagos_res.get("data"):
            pagos = pagos_res["data"]
            # Asegurar que pagos es una lista
            if not isinstance(pagos, list):
                pagos = []
            
            my_pagos = []
            for pago in pagos:
                if not isinstance(pago, dict):
                    continue
                
                # Intentar obtener el ID de la factura de diferentes formas
                factura_id = None
                factura = pago.get("factura")
                
                if isinstance(factura, dict):
                    factura_id = factura.get("id_factura") or factura.get("id")
                elif factura:
                    factura_id = factura
                
                # También verificar campo directo id_factura
                if not factura_id:
                    factura_id = pago.get("id_factura") or pago.get("factura_id")
                
                # Comparar IDs (convertir a int para comparación segura)
                if factura_id:
                    try:
                        factura_id_int = int(factura_id)
                        if any(int(fid) == factura_id_int for fid in factura_ids if fid):
                            my_pagos.append(pago)
                    except (ValueError, TypeError):
                        # Si no se puede convertir, comparar directamente
                        if factura_id in factura_ids:
                            my_pagos.append(pago)
            
            logger.info(f"get_my_pagos: cliente_id={cliente_id}, factura_ids={factura_ids}, encontrados {len(my_pagos)} pagos")
            return {"success": True, "data": my_pagos}
        
        return {"success": True, "data": []}
    
    def get_roles_empleado(self) -> Dict[str, Any]:
        """
        Obtiene todos los roles de empleado.
        
        Returns:
            Dict con 'success' y 'data' (lista de roles) o 'error'
        """
        # El endpoint es /roles según la documentación del backend
        return self.api._request("GET", "/roles")

