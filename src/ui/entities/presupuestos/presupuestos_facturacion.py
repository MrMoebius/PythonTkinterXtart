"""
Módulo de generación de facturas desde presupuestos.
Maneja la lógica de plazos y creación de facturas.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional


class PresupuestoFacturacion:
    """Clase para manejar la generación de facturas desde presupuestos."""
    
    def __init__(self, api, parent_window):
        """
        Args:
            api: Cliente REST para crear facturas
            parent_window: Ventana padre (tkinter widget) para crear modales
        """
        self.api = api
        self.parent_window = parent_window
    
    def abrir_ventana_generar_factura(
        self,
        presupuesto: Dict,
        cliente_nombre: str,
        productos_info: List[Dict],
        total: float,
        cliente_id: int,
        empleado_id: int,
        on_success_callback=None
    ):
        """
        Abre ventana modal para seleccionar plazos de pago y generar facturas.
        
        Args:
            presupuesto: Diccionario con datos del presupuesto
            cliente_nombre: Nombre del cliente
            productos_info: Lista de productos con nombre y precio
            total: Total del presupuesto
            cliente_id: ID del cliente pagador
            empleado_id: ID del empleado responsable
            on_success_callback: Función a llamar después de generar facturas exitosamente
        """
        presupuesto_id = presupuesto.get("id_Presupuesto") or presupuesto.get("id")
        
        # Verificar si el presupuesto ya tiene facturas asociadas
        if self._presupuesto_tiene_facturas(presupuesto_id):
            messagebox.showwarning(
                "Presupuesto ya facturado",
                f"El presupuesto #{presupuesto_id} ya tiene facturas asociadas.\n"
                "No se pueden generar facturas adicionales desde este presupuesto."
            )
            return
        
        modal = tk.Toplevel(self.parent_window)
        modal.title("Generar Factura desde Presupuesto")
        modal.geometry("650x400")
        modal.transient(self.parent_window.winfo_toplevel())
        modal.grab_set()
        
        # Centrar ventana
        modal.update_idletasks()
        x = (modal.winfo_screenwidth() // 2) - 325
        y = (modal.winfo_screenheight() // 2) - 210
        modal.geometry(f"650x400+{x}+{y}")
        
        # Frame principal
        main = ttk.Frame(modal, padding=15)
        main.pack(fill=tk.BOTH, expand=True)
        
        row = 0
        
        # Título
        ttk.Label(main, text="Generar Factura desde Presupuesto", font=("Arial", 14, "bold")).grid(
            row=row, column=0, columnspan=2, pady=(0, 15), sticky="w"
        )
        row += 1
        
        # Cliente
        ttk.Label(main, text="Cliente:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", pady=4)
        ttk.Label(main, text=cliente_nombre).grid(row=row, column=1, sticky="w", padx=10, pady=4)
        row += 1
        
        # Productos
        ttk.Label(main, text="Productos:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="nw", pady=4)
        productos_frame = ttk.Frame(main)
        productos_frame.grid(row=row, column=1, sticky="w", padx=10, pady=4)
        
        productos_text = "\n".join([f"• {p['nombre']}: €{p['precio']:.2f}" for p in productos_info])
        ttk.Label(productos_frame, text=productos_text, justify="left").pack(anchor="w")
        row += 1
        
        # Precio final
        ttk.Label(main, text="Precio Final:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", pady=8)
        ttk.Label(main, text=f"€{total:.2f}", font=("Arial", 12, "bold")).grid(row=row, column=1, sticky="w", padx=10, pady=8)
        row += 1
        
        # Separador
        ttk.Separator(main, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky="ew", pady=10)
        row += 1
        
        # Plazos
        ttk.Label(main, text="Plazos de Pago:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", pady=4)
        plazos_opts = ["Pago único", "3 meses", "6 meses", "9 meses"]
        combo_plazos = ttk.Combobox(main, values=plazos_opts, width=18, state="readonly")
        combo_plazos.set("Pago único")
        combo_plazos.grid(row=row, column=1, sticky="w", padx=10, pady=4)
        row += 1
        
        # Información de plazos (se actualiza dinámicamente)
        info_label = ttk.Label(main, text="", font=("Arial", 9), foreground="blue")
        info_label.grid(row=row, column=0, columnspan=2, sticky="w", pady=4)
        row += 1
        
        # Función para actualizar información de plazos
        def actualizar_info_plazos(event=None):
            seleccion = combo_plazos.get()
            if seleccion == "Pago único":
                info_label.config(text=f"Se generará 1 factura de €{total:.2f}")
            else:
                meses = int(seleccion.split()[0])
                precio_plazo = total / meses
                info_label.config(
                    text=f"Se generarán {meses} facturas de €{precio_plazo:.2f} cada una"
                )
        
        combo_plazos.bind("<<ComboboxSelected>>", actualizar_info_plazos)
        actualizar_info_plazos()  # Inicializar
        
        row += 1
        
        # Botones
        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=15)
        
        def aceptar():
            seleccion = combo_plazos.get()
            if seleccion == "Pago único":
                num_plazos = 1
            else:
                num_plazos = int(seleccion.split()[0])
            
            modal.destroy()
            self.generar_facturas_plazos(
                presupuesto_id, cliente_id, empleado_id, total, num_plazos, on_success_callback
            )
        
        def denegar():
            modal.destroy()
        
        ttk.Button(btn_frame, text="Aceptar", command=aceptar).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Denegar", command=denegar).pack(side=tk.LEFT, padx=10)
    
    def generar_facturas_plazos(
        self,
        presupuesto_id: int,
        cliente_id: int,
        empleado_id: int,
        total: float,
        num_plazos: int,
        on_success_callback=None
    ):
        """
        Genera las facturas según el número de plazos seleccionado usando el endpoint del backend.
        
        Args:
            presupuesto_id: ID del presupuesto
            cliente_id: ID del cliente pagador (no se usa, el backend lo obtiene del presupuesto)
            empleado_id: ID del empleado responsable (no se usa, el backend lo obtiene del presupuesto)
            total: Total a facturar (no se usa, el backend lo obtiene del presupuesto)
            num_plazos: Número de plazos (1, 3, 6, 9)
            on_success_callback: Función a llamar después de generar facturas exitosamente
        """
        try:
            # Llamar al endpoint del backend para generar facturas
            # POST /presupuestos/{id}/generar-facturas
            url = f"/presupuestos/{presupuesto_id}/generar-facturas"
            payload = {"num_plazos": num_plazos}
            
            res = self.api._request("POST", url, json=payload)
            
            if res.get("success"):
                facturas = res.get("data", [])
                
                # Construir mensaje de éxito
                mensaje = f"Se generaron {len(facturas)} facturas correctamente:\n\n"
                for factura in facturas:
                    num_factura = factura.get("num_factura", "N/A")
                    fecha = factura.get("fecha", factura.get("fecha_emision", "N/A"))
                    total_factura = factura.get("total", 0)
                    mensaje += f"• {num_factura} - {fecha}: €{total_factura:.2f}\n"
                
                messagebox.showinfo("Éxito", mensaje)
                
                # Llamar callback si existe
                if on_success_callback:
                    on_success_callback()
            else:
                error_msg = res.get("error", "Error desconocido")
                messagebox.showerror("Error", f"Error al generar facturas:\n{error_msg}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar facturas:\n{str(e)}")
    
    def _presupuesto_tiene_facturas(self, presupuesto_id: int) -> bool:
        """
        Verifica si un presupuesto ya tiene facturas asociadas.
        
        Args:
            presupuesto_id: ID del presupuesto a verificar
            
        Returns:
            True si el presupuesto ya tiene facturas, False en caso contrario
        """
        try:
            # Obtener todas las facturas
            result = self.api.get_all("facturas")
            if not result.get("success"):
                return False
            
            facturas = result.get("data", [])
            if not isinstance(facturas, list):
                return False
            
            # Buscar facturas que mencionen este presupuesto en las notas
            for factura in facturas:
                notas = factura.get("notas", "")
                if isinstance(notas, str) and f"presupuesto #{presupuesto_id}" in notas.lower():
                    return True
            
            return False
        except Exception:
            # En caso de error, permitir intentar (el backend también validará)
            return False


# Función calcular_fechas_plazos eliminada - ahora el backend calcula las fechas

