"""
Módulo de filtrado de pagos.
Maneja la lógica de filtrado local por nombre de cliente.
"""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def normalize_pago_data(pago: Dict, clientes: List[Dict], facturas: List[Dict]) -> Dict:
    """
    Normaliza los datos de un pago agregando información del cliente y factura.
    
    Args:
        pago: Diccionario con datos del pago
        clientes: Lista de clientes para resolver relaciones
        facturas: Lista de facturas para resolver relaciones
    
    Returns:
        Diccionario con pago normalizado
    """
    if not isinstance(pago, dict):
        return pago
    
    # Normalizar ID de pago
    if "id_pago" in pago and "id" not in pago:
        pago["id"] = pago["id_pago"]
    
    # Extraer factura_id de objeto anidado o campo directo
    factura_obj = pago.get("factura")
    if isinstance(factura_obj, dict):
        pago["factura_id"] = factura_obj.get("id_factura") or factura_obj.get("id")
    elif "id_factura" in pago:
        pago["factura_id"] = pago["id_factura"]
    elif "factura_id" not in pago:
        pago["factura_id"] = None
    
    # Extraer cliente_id de objeto anidado o campo directo
    cliente_obj = pago.get("cliente_pagador") or pago.get("cliente")
    if isinstance(cliente_obj, dict):
        pago["cliente_id"] = cliente_obj.get("id_cliente") or cliente_obj.get("id")
    elif "id_cliente" in pago:
        pago["cliente_id"] = pago["id_cliente"]
    elif "cliente_id" not in pago:
        pago["cliente_id"] = None
    
    # Agregar nombre del cliente
    cliente_id = pago.get("cliente_id")
    if cliente_id:
        cliente = _find_cliente(clientes, cliente_id)
        if cliente:
            nombre = cliente.get("nombre", "")
            apellidos = cliente.get("apellidos", "")
            if apellidos:
                pago["cliente_nombre"] = f"{nombre} {apellidos}".strip()
            else:
                pago["cliente_nombre"] = nombre or cliente.get("razon_social", "N/A")
        else:
            pago["cliente_nombre"] = f"ID {cliente_id}"
    else:
        pago["cliente_nombre"] = "N/A"
    
    return pago


def filter_pagos_by_cliente(
    pagos: List[Dict],
    clientes: List[Dict],
    facturas: List[Dict],
    filter_values: Dict
) -> List[Dict]:
    """
    Filtra pagos por nombre de cliente.
    
    Args:
        pagos: Lista de pagos a filtrar
        clientes: Lista de clientes para resolver relaciones
        facturas: Lista de facturas para resolver relaciones
        filter_values: Diccionario con valores de filtro (ej: {"cliente_nombre": "Juan"})
    
    Returns:
        Lista de pagos filtrados
    """
    # Si no hay filtros, retornar todos normalizados
    if not filter_values or not any(v and str(v).strip() for v in filter_values.values()):
        logger.info("No hay filtros, retornando todos los datos normalizados")
        return [normalize_pago_data(p.copy(), clientes, facturas) for p in pagos]
    
    # Normalizar todos los pagos primero
    normalized_pagos = [normalize_pago_data(p.copy(), clientes, facturas) for p in pagos]
    
    # Aplicar filtros
    filtered_data = []
    for row in normalized_pagos:
        if not isinstance(row, dict):
            continue
        
        # Filtro por nombre de cliente
        if "cliente_nombre" in filter_values and filter_values.get("cliente_nombre"):
            nombre_filter = filter_values["cliente_nombre"].strip().lower()
            cliente_nombre = str(row.get("cliente_nombre", "")).strip().lower()
            if nombre_filter not in cliente_nombre:
                continue
        
        filtered_data.append(row)
    
    return filtered_data


def _find_cliente(clientes: List[Dict], cliente_id: Optional[int]) -> Optional[Dict]:
    """Busca un cliente por ID en la lista de clientes."""
    if not cliente_id:
        return None
    return next(
        (c for c in clientes if c.get("id") == cliente_id or c.get("id_cliente") == cliente_id),
        None
    )

