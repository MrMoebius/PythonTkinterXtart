"""
Módulo de exportación de pagos a PDF/PNG.
"""

from typing import Dict, List, Optional
import matplotlib.pyplot as plt

from src.utils.export_helpers import DocumentExporter, create_document_base
from src.reports.exporters.pdf_exporter import PDFExporter
from src.reports.exporters.image_exporter import ImageExporter


class PagoExporter:
    """Clase para exportar pagos a PDF o PNG."""
    
    def __init__(self, api, clientes: List[Dict], facturas: List[Dict]):
        """
        Args:
            api: Cliente REST para obtener datos del backend
            clientes: Lista de clientes para resolver relaciones
            facturas: Lista de facturas para resolver relaciones
        """
        self.api = api
        self.clientes = clientes
        self.facturas = facturas
    
    def export_pdf(self, pago_data: Dict, path: str):
        """Exporta el pago a PDF."""
        self._generate_document(pago_data, path, "pdf")
    
    def export_png(self, pago_data: Dict, path: str):
        """Exporta el pago a PNG."""
        self._generate_document(pago_data, path, "png")
    
    def _generate_document(self, pago_data: Dict, path: str, format: str):
        """Genera un documento PDF o PNG con los datos del pago."""
        pago_id = pago_data.get("id_pago") or pago_data.get("id")
        if not pago_id:
            raise ValueError("No se pudo obtener el ID del pago")
        
        # Obtener pago completo del backend
        result = self.api.get_by_id("pagos", pago_id)
        if not result.get("success"):
            raise ValueError(f"Error al obtener pago: {result.get('error', 'Error desconocido')}")
        
        pago = result.get("data", {})
        if not isinstance(pago, dict):
            raise ValueError("Datos del pago inválidos")
        
        # Obtener datos relacionados
        factura_id = pago.get("id_factura") or pago.get("factura_id")
        cliente_id = pago.get("id_cliente") or pago.get("cliente_id")
        
        factura = self._find_factura(factura_id)
        cliente = self._find_cliente(cliente_id)
        
        # Crear documento base
        fig, ax = create_document_base()
        exporter = DocumentExporter(fig, ax)
        
        # Logo y título
        exporter.add_logo()
        exporter.add_main_title("COMPROBANTE DE PAGO", f"Número: {pago_id}")

        # INFORMACIÓN DEL PAGO
        fecha_pago = pago.get("fecha") or pago.get("fecha_pago", "N/A")
        exporter.create_section("INFORMACIÓN DEL PAGO", [
            ("Fecha", fecha_pago),
            ("Importe", f"€{pago.get('importe', 0):.2f}"),
            ("Método de Pago", str(pago.get("metodo_pago", "N/A")).title()),
            ("Estado", str(pago.get("estado", "N/A")).title())
        ])

        # FACTURA ASOCIADA
        factura_items = self._build_factura_items(factura, factura_id)
        exporter.create_section("FACTURA ASOCIADA", factura_items)

        # CLIENTE
        cliente_items = self._build_cliente_items(cliente, cliente_id)
        exporter.create_section("CLIENTE", cliente_items)
        
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
    
    def _find_factura(self, factura_id: Optional[int]) -> Optional[Dict]:
        """Busca una factura por ID en la lista de facturas."""
        if not factura_id:
            return None
        return next(
            (f for f in self.facturas if f.get("id") == factura_id or f.get("id_factura") == factura_id),
            None
        )
    
    def _build_factura_items(self, factura: Optional[Dict], factura_id: Optional[int]) -> List[tuple]:
        """Construye la lista de items para mostrar información de la factura."""
        if factura:
            num_factura = factura.get("num_factura", factura.get("id", "N/A"))
            fecha_factura = factura.get("fecha") or factura.get("fecha_emision", "N/A")
            return [
                ("Número", num_factura),
                ("Total", f"€{factura.get('total', 0):.2f}"),
                ("Fecha", fecha_factura)
            ]
        else:
            return [("ID", factura_id)]
    
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

