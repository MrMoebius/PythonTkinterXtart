"""
Módulo de filtrado de presupuestos.
Maneja la lógica de filtrado local por nombre de cliente.
"""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def normalize_presupuesto_data(presupuesto: Dict, clientes: List[Dict], normalize_estado_func=None) -> Dict:
    if not isinstance(presupuesto, dict):
        return presupuesto
    
    if "id_Presupuesto" in presupuesto and "id" not in presupuesto:
        presupuesto["id"] = presupuesto["id_Presupuesto"]
    
    if presupuesto.get("estado"):
        presupuesto["estado"] = presupuesto["estado"].upper().strip()
    
    # Agregar datos del cliente pagador
    cliente_pagador_id = presupuesto.get("id_cliente_pagador")
    if cliente_pagador_id:
        cliente = _find_cliente(clientes, cliente_pagador_id)
        if cliente:
            presupuesto["cliente_nombre"] = cliente.get("nombre", "N/A")
            presupuesto["_cliente_email"] = cliente.get("email", "")
            presupuesto["_cliente_telefono"] = cliente.get("telefono", "")
        else:
            presupuesto["cliente_nombre"] = f"ID {cliente_pagador_id}"
            presupuesto["_cliente_email"] = ""
            presupuesto["_cliente_telefono"] = ""
    else:
        # Intentar obtenerlo con get_by_id si no viene en la respuesta
        presupuesto_id = presupuesto.get("id")
        if presupuesto_id:
            # Nota: Esta lógica requiere acceso a la API, se manejará en la clase
            presupuesto["cliente_nombre"] = "N/A"
            presupuesto["_cliente_email"] = ""
            presupuesto["_cliente_telefono"] = ""
        else:
            presupuesto["cliente_nombre"] = "N/A"
            presupuesto["_cliente_email"] = ""
            presupuesto["_cliente_telefono"] = ""
    
    return presupuesto


def filter_presupuestos_by_cliente(
    presupuestos: List[Dict],
    clientes: List[Dict],
    filter_values: Dict,
    api,
    normalize_estado_func=None
) -> List[Dict]:
    if not filter_values or not any(v and str(v).strip() for v in filter_values.values()):
        logger.info("No hay filtros, retornando todos los datos normalizados")
        return [normalize_presupuesto_data(p, clientes) for p in presupuestos]
    
    normalized_presupuestos = []
    for presupuesto in presupuestos:
        if not isinstance(presupuesto, dict):
            continue
        
        normalized = normalize_presupuesto_data(presupuesto.copy(), clientes)
        
        # Si no tiene cliente_pagador_id pero tiene id, intentar obtenerlo del backend
        if not normalized.get("id_cliente_pagador") and normalized.get("id"):
            try:
                presupuesto_completo = api.get_by_id("presupuestos", normalized.get("id"))
                if presupuesto_completo.get("success"):
                    presup_data = presupuesto_completo.get("data", {})
                    if isinstance(presup_data, dict):
                        cliente_pagador_id = presup_data.get("id_cliente_pagador")
                        if cliente_pagador_id:
                            cliente = _find_cliente(clientes, cliente_pagador_id)
                            if cliente:
                                normalized["cliente_nombre"] = cliente.get("nombre", "N/A")
                                normalized["_cliente_email"] = cliente.get("email", "")
                                normalized["_cliente_telefono"] = cliente.get("telefono", "")
                            else:
                                normalized["cliente_nombre"] = f"ID {cliente_pagador_id}"
                                normalized["_cliente_email"] = ""
                                normalized["_cliente_telefono"] = ""
            except Exception as e:
                logger.warning(f"Error al obtener presupuesto completo: {e}")
        
        normalized_presupuestos.append(normalized)
    
    # Aplicar filtros
    filtered_data = []
    for row in normalized_presupuestos:
        if not isinstance(row, dict):
            continue
        
        # Filtro por nombre
        if "nombre" in filter_values and filter_values.get("nombre"):
            nombre_filter = filter_values["nombre"].strip().lower()
            cliente_nombre = row.get("cliente_nombre", "").lower()
            cliente_email = row.get("_cliente_email", "").lower()
            cliente_telefono = row.get("_cliente_telefono", "").lower()
            
            if (nombre_filter in cliente_nombre or 
                nombre_filter in cliente_email or 
                nombre_filter in cliente_telefono):
                filtered_data.append(row)
        else:
            # Si no hay filtro de nombre, incluir todos
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

