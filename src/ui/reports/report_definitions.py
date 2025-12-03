"""
Definiciones de informes disponibles.
Mapea nombres de informes a métodos del ReportLoader y tipos de gráficos.
"""

from typing import Dict, Callable, Optional, Tuple, List


# Configuración de cada informe
REPORT_CONFIGS: Dict[str, Dict] = {
    "Ventas por empleado": {
        "loader_method": "ventas_por_empleado",
        "chart_type": "bar",
        "chart_config": {
            "xlabel": "Empleado",
            "ylabel": "Total (€)",
            "data_extractor": lambda data: (
                [x["nombre"] for x in data],
                [x["total"] for x in data]
            )
        }
    },
    "Estado presupuestos": {
        "loader_method": "estados_presupuestos",
        "chart_type": "pie",
        "chart_config": {
            "data_extractor": lambda data: (
                list(data.keys()),
                list(data.values())
            )
        }
    },
    "Facturación mensual": {
        "loader_method": "facturacion_mensual",
        "chart_type": "line",
        "chart_config": {
            "xlabel": "Mes",
            "ylabel": "€",
            "data_extractor": lambda data: (
                sorted(data.keys()),
                [data[m] for m in sorted(data.keys())]
            )
        }
    },
    "Ventas por producto": {
        "loader_method": "ventas_por_producto",
        "chart_type": "bar",
        "chart_config": {
            "xlabel": "Producto",
            "ylabel": "Total (€)",
            "data_extractor": lambda data: (
                [x["producto"] for x in data],
                [x["total"] for x in data]
            )
        }
    },
    "Ratio conversión": {
        "loader_method": "ratio_conversion",
        "chart_type": "pie",
        "chart_config": {
            "data_extractor": lambda data: (
                list(data.keys()),
                list(data.values())
            )
        }
    }
}


def get_report_options() -> List[str]:
    """Retorna la lista de nombres de informes disponibles."""
    return list(REPORT_CONFIGS.keys())


def get_report_config(report_name: str) -> Optional[Dict]:
    """
    Obtiene la configuración de un informe por su nombre.
    
    Args:
        report_name: Nombre del informe
    
    Returns:
        Diccionario con configuración o None si no existe
    """
    return REPORT_CONFIGS.get(report_name)


def get_loader_method_name(report_name: str) -> Optional[str]:
    """
    Obtiene el nombre del método del ReportLoader para un informe.
    
    Args:
        report_name: Nombre del informe
    
    Returns:
        Nombre del método o None si no existe
    """
    config = get_report_config(report_name)
    return config.get("loader_method") if config else None


def get_chart_type(report_name: str) -> Optional[str]:
    """
    Obtiene el tipo de gráfico para un informe.
    
    Args:
        report_name: Nombre del informe
    
    Returns:
        Tipo de gráfico ("bar", "pie", "line") o None si no existe
    """
    config = get_report_config(report_name)
    return config.get("chart_type") if config else None


def get_chart_config(report_name: str) -> Optional[Dict]:
    """
    Obtiene la configuración del gráfico para un informe.
    
    Args:
        report_name: Nombre del informe
    
    Returns:
        Diccionario con configuración del gráfico o None si no existe
    """
    config = get_report_config(report_name)
    return config.get("chart_config") if config else None

