"""
Módulo de filtrado de facturas.
Maneja la lógica de filtrado local por nombre de cliente.
"""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def normalize_factura_data(factura: Dict, clientes: List[Dict]) -> Dict:
    """
    Normaliza los datos de una factura agregando información del cliente.
    
    Args:
        factura: Diccionario con datos de la factura
        clientes: Lista de clientes para resolver relaciones
    
    Returns:
        Diccionario con factura normalizada
    """
    if not isinstance(factura, dict):
        return factura
    
    # Normalizar ID de factura
    if "id_factura" in factura and "id" not in factura:
        factura["id"] = factura["id_factura"]
    
    # Extraer cliente_id de objeto anidado o campo directo
    cliente_obj = factura.get("cliente_pagador") or factura.get("cliente")
    if isinstance(cliente_obj, dict):
        factura["cliente_id"] = cliente_obj.get("id_cliente") or cliente_obj.get("id")
    elif "id_cliente" in factura:
        factura["cliente_id"] = factura["id_cliente"]
    elif "cliente_id" not in factura:
        factura["cliente_id"] = None
    
    # Extraer empleado_id
    empleado_obj = factura.get("empleado") or factura.get("empleado_responsable")
    if isinstance(empleado_obj, dict):
        factura["empleado_id"] = empleado_obj.get("id_empleado") or empleado_obj.get("id")
    elif "id_empleado" in factura:
        factura["empleado_id"] = factura["id_empleado"]
    elif "empleado_id" not in factura:
        factura["empleado_id"] = None
    
    # Agregar nombre del cliente
    cliente_id = factura.get("cliente_id")
    if cliente_id:
        cliente = _find_cliente(clientes, cliente_id)
        if cliente:
            factura["cliente_nombre"] = cliente.get("nombre", "N/A")
        else:
            factura["cliente_nombre"] = f"ID {cliente_id}"
    else:
        factura["cliente_nombre"] = "N/A"
    
    return factura


def filter_facturas_by_cliente(
    facturas: List[Dict],
    clientes: List[Dict],
    filter_values: Dict
) -> List[Dict]:
    """
    Filtra facturas por nombre de cliente.
    
    Args:
        facturas: Lista de facturas a filtrar
        clientes: Lista de clientes para resolver relaciones
        filter_values: Diccionario con valores de filtro (ej: {"cliente_nombre": "Juan"})
    
    Returns:
        Lista de facturas filtradas
    """
    # Si no hay filtros, retornar todos normalizados
    if not filter_values or not any(v and str(v).strip() for v in filter_values.values()):
        logger.info("No hay filtros, retornando todos los datos normalizados")
        return [normalize_factura_data(f.copy(), clientes) for f in facturas]
    
    # Normalizar todas las facturas primero
    normalized_facturas = [normalize_factura_data(f.copy(), clientes) for f in facturas]
    
    # Aplicar filtros
    filtered_data = []
    for row in normalized_facturas:
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

