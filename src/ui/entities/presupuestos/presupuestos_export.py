"""
Módulo de exportación de presupuestos a PDF/PNG.
"""

from typing import Dict, List, Optional
import matplotlib.pyplot as plt

from src.utils.export_helpers import DocumentExporter, create_document_base
from src.reports.exporters.pdf_exporter import PDFExporter
from src.reports.exporters.image_exporter import ImageExporter


class PresupuestoExporter:
    """Clase para exportar presupuestos a PDF o PNG."""
    
    def __init__(self, api, clientes: List[Dict], empleados: List[Dict], productos: List[Dict]):
        """
        Args:
            api: Cliente REST para obtener datos del backend
            clientes: Lista de clientes para resolver relaciones
            empleados: Lista de empleados para resolver relaciones
            productos: Lista de productos para resolver relaciones
        """
        self.api = api
        self.clientes = clientes
        self.empleados = empleados
        self.productos = productos
    
    def export_pdf(self, presupuesto_data: Dict, path: str):
        """Exporta el presupuesto a PDF."""
        self._generate_document(presupuesto_data, path, "pdf")
    
    def export_png(self, presupuesto_data: Dict, path: str):
        """Exporta el presupuesto a PNG."""
        self._generate_document(presupuesto_data, path, "png")
    
    def _generate_document(self, presupuesto_data: Dict, path: str, format: str):
        """Genera un documento PDF o PNG con los datos del presupuesto."""
        # Obtener datos completos del presupuesto
        presupuesto_id = presupuesto_data.get("id_Presupuesto") or presupuesto_data.get("id")
        if not presupuesto_id:
            raise ValueError("No se pudo obtener el ID del presupuesto")
        
        # Obtener presupuesto completo del backend
        result = self.api.get_by_id("presupuestos", presupuesto_id)
        if not result.get("success"):
            raise ValueError(f"Error al obtener presupuesto: {result.get('error', 'Error desconocido')}")
        
        presupuesto = result.get("data", {})
        if not isinstance(presupuesto, dict):
            raise ValueError("Datos del presupuesto inválidos")
        
        # Obtener datos relacionados
        cliente_pagador_id = presupuesto.get("id_cliente_pagador")
        cliente_beneficiario_id = presupuesto.get("id_cliente_beneficiario")
        empleado_id = presupuesto.get("id_empleado")
        
        # Obtener productos del presupuesto (nuevo formato con presupuestoProductos)
        presupuesto_productos = presupuesto.get("presupuestoProductos") or presupuesto.get("presupuesto_productos") or []
        
        cliente_pagador = self._find_cliente(cliente_pagador_id)
        cliente_beneficiario = self._find_cliente(cliente_beneficiario_id)
        empleado = self._find_empleado(empleado_id)
        
        # Crear documento base
        fig, ax = create_document_base()
        exporter = DocumentExporter(fig, ax)
        
        # Logo y título
        exporter.add_logo()
        exporter.add_main_title("PRESUPUESTO", f"Número: {presupuesto_id}")

        # INFORMACIÓN DEL PRESUPUESTO
        exporter.create_section("RESUMEN", [
            ("Estado", presupuesto.get("estado", "N/A")),
            ("Fecha Apertura", presupuesto.get("fecha_apertura", "N/A")),
            ("Fecha Cierre", presupuesto.get("fecha_cierre") or "-"),
            ("Total", f"€{presupuesto.get('presupuesto', 0):.2f}")
        ])

        # CLIENTE PAGADOR
        cliente_pagador_items = self._build_cliente_items(cliente_pagador, cliente_pagador_id)
        exporter.create_section("CLIENTE PAGADOR", cliente_pagador_items)

        # CLIENTE BENEFICIARIO
        cliente_beneficiario_items = self._build_cliente_items(cliente_beneficiario, cliente_beneficiario_id, include_tipo=False)
        exporter.create_section("CLIENTE BENEFICIARIO", cliente_beneficiario_items)

        # EMPLEADO RESPONSABLE
        empleado_items = self._build_empleado_items(empleado, empleado_id)
        exporter.create_section("EMPLEADO RESPONSABLE", empleado_items)

        # PRODUCTOS — TABLA
        self._add_productos_table(exporter, presupuesto_productos)

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
    
    def _find_producto(self, producto_id: Optional[int]) -> Optional[Dict]:
        """Busca un producto por ID en la lista de productos."""
        if not producto_id:
            return None
        return next(
            (p for p in self.productos if p.get("id") == producto_id or p.get("id_producto") == producto_id),
            None
        )
    
    def _build_cliente_items(self, cliente: Optional[Dict], cliente_id: Optional[int], include_tipo: bool = True) -> List[tuple]:
        """Construye la lista de items para mostrar información del cliente."""
        if cliente:
            items = [
                ("Nombre", cliente.get("nombre", "N/A")),
                ("Email", cliente.get("email", "N/A")),
                ("Teléfono", cliente.get("telefono", "N/A"))
            ]
            if include_tipo:
                items.append(("Tipo", cliente.get("tipo_cliente", "N/A")))
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
    
    def _add_productos_table(self, exporter: DocumentExporter, presupuesto_productos: List[Dict]):
        """Añade la tabla de productos al documento."""
        exporter.separator()    
        exporter.ax.text(0.5, exporter.y_position, "PRODUCTOS",
                ha="right", fontsize=13, weight='bold', transform=exporter.ax.transAxes)
        exporter.y_position -= 0.032

        if not presupuesto_productos:
            exporter.ax.text(0.5, exporter.y_position, "No hay productos asociados",
                    ha="center", fontsize=10, style='italic', transform=exporter.ax.transAxes)
            exporter.y_position -= 0.04
            return

        # Preparar datos de la tabla
        table_data = []
        total_general = 0.0
        
        for pp in presupuesto_productos:
            if not isinstance(pp, dict):
                continue
                
            producto_id = pp.get("id_producto")
            cantidad = pp.get("cantidad", 1)
            precio_unitario = pp.get("precio_unitario", 0)
            subtotal = pp.get("subtotal", precio_unitario * cantidad)
            total_general += subtotal
            
            # Buscar producto para obtener nombre
            producto = self._find_producto(producto_id)
            nombre_producto = producto.get("nombre", f"Producto ID: {producto_id}") if producto else f"Producto ID: {producto_id}"
            
            table_data.append([
                nombre_producto,
                f"{cantidad}",
                f"€{precio_unitario:.2f}",
                f"€{subtotal:.2f}"
            ])

        if not table_data:
            exporter.ax.text(0.5, exporter.y_position, "No hay productos válidos",
                    ha="center", fontsize=10, style='italic', transform=exporter.ax.transAxes)
            exporter.y_position -= 0.04
            return

        # Agregar fila de total
        table_data.append(["", "", "TOTAL:", f"€{total_general:.2f}"])

        # Calcular altura de la tabla según número de productos
        num_filas = len(table_data)
        altura_tabla = min(0.05 * num_filas + 0.08, 0.35)  # Máximo 35% de altura

        table = exporter.ax.table(
            cellText=table_data,
            colLabels=["Producto", "Cantidad", "Precio Unit.", "Subtotal"],
            cellLoc="left",
            colWidths=[0.35, 0.12, 0.15, 0.15],
            loc="center",
            bbox=[0.10, exporter.y_position - altura_tabla, 0.80, altura_tabla]
        )

        table.auto_set_font_size(False)
        table.set_fontsize(9)
        
        # Resaltar fila de total
        if num_filas > 0:
            for i in range(4):
                table[(num_filas, i)].set_facecolor('#E8E8E8')
                table[(num_filas, i)].set_text_props(weight='bold')

        # Tarjeta alrededor de la tabla
        exporter.draw_card(exporter.y_position + 0.018, exporter.y_position - altura_tabla - 0.02)
        exporter.y_position -= altura_tabla + 0.03

