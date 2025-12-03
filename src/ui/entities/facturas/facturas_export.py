"""
Módulo de exportación de facturas a PDF/PNG.
"""

from typing import Dict, List, Optional
import matplotlib.pyplot as plt

from src.utils.export_helpers import DocumentExporter, create_document_base
from src.reports.exporters.pdf_exporter import PDFExporter
from src.reports.exporters.image_exporter import ImageExporter


class FacturaExporter:
    """Clase para exportar facturas a PDF o PNG."""
    
    def __init__(self, api, clientes: List[Dict], empleados: List[Dict]):
        """
        Args:
            api: Cliente REST para obtener datos del backend
            clientes: Lista de clientes para resolver relaciones
            empleados: Lista de empleados para resolver relaciones
        """
        self.api = api
        self.clientes = clientes
        self.empleados = empleados
    
    def export_pdf(self, factura_data: Dict, path: str):
        """Exporta la factura a PDF."""
        self._generate_document(factura_data, path, "pdf")
    
    def export_png(self, factura_data: Dict, path: str):
        """Exporta la factura a PNG."""
        self._generate_document(factura_data, path, "png")
    
    def _generate_document(self, factura_data: Dict, path: str, format: str):
        """Genera un documento PDF o PNG con los datos de la factura."""
        factura_id = factura_data.get("id_factura") or factura_data.get("id")
        if not factura_id:
            raise ValueError("No se pudo obtener el ID de la factura")
        
        # Obtener factura completa del backend
        result = self.api.get_by_id("facturas", factura_id)
        if not result.get("success"):
            raise ValueError(f"Error al obtener factura: {result.get('error', 'Error desconocido')}")
        
        factura = result.get("data", {})
        if not isinstance(factura, dict):
            raise ValueError("Datos de la factura inválidos")
        
        # Obtener datos relacionados
        cliente_id = factura.get("id_cliente") or factura.get("cliente_id")
        empleado_id = factura.get("id_empleado") or factura.get("empleado_id")
        
        cliente = self._find_cliente(cliente_id)
        empleado = self._find_empleado(empleado_id)
        
        # Crear documento base
        fig, ax = create_document_base()
        exporter = DocumentExporter(fig, ax)
        
        # Logo y título
        exporter.add_logo()
        num_factura = factura.get("num_factura", factura_id)
        exporter.add_main_title("FACTURA", f"Número: {num_factura}")

        # INFORMACIÓN DE LA FACTURA
        factura_items = [
            ("Fecha", factura.get("fecha") or factura.get("fecha_emision", "N/A")),
            ("Total", f"€{factura.get('total', 0):.2f}"),
            ("Estado", factura.get("estado", "N/A"))
        ]
        notas = factura.get("notas", "")
        if notas:
            factura_items.append(("Notas", notas))
        exporter.create_section("INFORMACIÓN DE LA FACTURA", factura_items)

        # CLIENTE
        cliente_items = self._build_cliente_items(cliente, cliente_id)
        exporter.create_section("CLIENTE", cliente_items)

        # EMPLEADO RESPONSABLE
        empleado_items = self._build_empleado_items(empleado, empleado_id)
        exporter.create_section("EMPLEADO RESPONSABLE", empleado_items)
        
        # Exportar
        if format == "pdf":
            PDFExporter.export(fig, path)
        else:
            ImageExporter.export(fig, path)
        
        plt.close(fig)
    
    def _find_cliente(self, cliente_id: Optional[int]) -> Optional[Dict]:
        """Busca un cliente por ID en la lista de clientes."""
        if not cliente_id:
            return None
        return next(
            (c for c in self.clientes if c.get("id") == cliente_id or c.get("id_cliente") == cliente_id),
            None
        )
    
    def _find_empleado(self, empleado_id: Optional[int]) -> Optional[Dict]:
        """Busca un empleado por ID en la lista de empleados."""
        if not empleado_id:
            return None
        return next(
            (e for e in self.empleados if e.get("id") == empleado_id or e.get("id_empleado") == empleado_id),
            None
        )
    
    def _build_cliente_items(self, cliente: Optional[Dict], cliente_id: Optional[int]) -> List[tuple]:
        """Construye la lista de items para mostrar información del cliente."""
        if cliente:
            items = [
                ("Nombre", cliente.get("nombre", "N/A")),
                ("Email", cliente.get("email", "N/A")),
                ("Teléfono", cliente.get("telefono", "N/A"))
            ]
            tipo_cliente = cliente.get("tipo_cliente")
            if tipo_cliente:
                items.append(("Tipo", tipo_cliente))
            return items
        else:
            return [("ID", cliente_id)]
    
    def _build_empleado_items(self, empleado: Optional[Dict], empleado_id: Optional[int]) -> List[tuple]:
        """Construye la lista de items para mostrar información del empleado."""
        if empleado:
            return [
                ("Nombre", empleado.get("nombre", "N/A")),
                ("Email", empleado.get("email", "N/A"))
            ]
        else:
            return [("ID", empleado_id)]

