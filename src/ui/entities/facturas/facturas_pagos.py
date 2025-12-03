"""
Módulo de procesamiento de pagos de facturas.
Maneja la lógica de creación de pagos y actualización de facturas.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional
from datetime import datetime


class FacturaPagoHandler:
    """Clase para manejar el procesamiento de pagos de facturas."""
    
    def __init__(self, api, parent_window):
        """
        Args:
            api: Cliente REST para crear pagos y actualizar facturas
            parent_window: Ventana padre (tkinter widget) para crear modales
        """
        self.api = api
        self.parent_window = parent_window
    
    def abrir_ventana_pago(
        self,
        factura_id: int,
        cliente_id: int,
        cliente_nombre: str,
        num_factura: str,
        total: float,
        fecha: str,
        estado: str,
        on_success_callback=None
    ):
        """
        Abre ventana modal para procesar el pago de una factura.
        
        Args:
            factura_id: ID de la factura
            cliente_id: ID del cliente
            cliente_nombre: Nombre del cliente
            num_factura: Número de factura
            total: Total a pagar
            fecha: Fecha de la factura
            estado: Estado actual de la factura
            on_success_callback: Función a llamar después de procesar el pago exitosamente
        """
        modal = tk.Toplevel(self.parent_window)
        modal.title("Pagar Factura")
        modal.geometry("450x480")
        modal.transient(self.parent_window.winfo_toplevel())
        modal.grab_set()
        
        # Centrar ventana
        modal.update_idletasks()
        x = (modal.winfo_screenwidth() // 2) - 300
        y = (modal.winfo_screenheight() // 2) - 240
        modal.geometry(f"500x480+{x}+{y}")
        
        # Frame principal
        main = ttk.Frame(modal, padding=15)
        main.pack(fill=tk.BOTH, expand=True)
        
        row = 0
        
        # Título
        ttk.Label(main, text="Pagar Factura", font=("Arial", 14, "bold")).grid(
            row=row, column=0, columnspan=2, pady=(0, 15), sticky="w"
        )
        row += 1
        
        # Resumen de la factura
        ttk.Label(main, text="Resumen de la Factura:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(0, 5)
        )
        row += 1
        
        # Frame para el resumen
        resumen_frame = ttk.LabelFrame(main, text="Datos de la Factura", padding=10)
        resumen_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        row += 1
        
        resumen_text = (
            f"Número de Factura: {num_factura}\n"
            f"Cliente: {cliente_nombre}\n"
            f"Fecha: {fecha}\n"
            f"Total: €{total:.2f}\n"
            f"Estado: {estado}"
        )
        ttk.Label(resumen_frame, text=resumen_text, justify="left").pack(anchor="w")
        
        # Checkbox para confirmar pago
        var_confirmar = tk.BooleanVar()
        check_confirmar = ttk.Checkbutton(
            main, 
            text="Confirmo que deseo realizar el pago de esta factura",
            variable=var_confirmar
        )
        check_confirmar.grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 15))
        row += 1
        
        # Método de pago
        ttk.Label(main, text="Método de Pago:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, sticky="w", pady=(0, 5)
        )
        # Métodos válidos según el backend (en minúsculas)
        metodos_pago = ["transferencia", "tarjeta", "efectivo"]
        combo_metodo = ttk.Combobox(main, values=metodos_pago, width=20, state="readonly")
        combo_metodo.set(metodos_pago[0])  # Por defecto: transferencia
        combo_metodo.grid(row=row, column=1, sticky="w", padx=10, pady=(0, 5))
        row += 1
        
        # Botones
        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=(20, 0))
        
        def aceptar():
            if not var_confirmar.get():
                messagebox.showwarning("Advertencia", "Debe confirmar el pago marcando la casilla")
                return
            
            metodo_seleccionado = combo_metodo.get()
            if not metodo_seleccionado:
                messagebox.showwarning("Advertencia", "Debe seleccionar un método de pago")
                return
            
            modal.destroy()
            self.procesar_pago(factura_id, total, metodo_seleccionado, on_success_callback)
        
        def cancelar():
            modal.destroy()
        
        ttk.Button(btn_frame, text="Aceptar", command=aceptar).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Cancelar", command=cancelar).pack(side=tk.LEFT, padx=10)
    
    def procesar_pago(
        self,
        factura_id: int,
        total: float,
        metodo_pago: str,
        on_success_callback=None
    ):
        """
        Procesa el pago de la factura creando un registro de pago y actualizando la factura.
        
        Args:
            factura_id: ID de la factura
            cliente_id: ID del cliente
            total: Importe del pago
            metodo_pago: Método de pago seleccionado
            on_success_callback: Función a llamar después de procesar el pago exitosamente
        """
        try:
            # Preparar datos del pago
            fecha_pago = datetime.now().strftime("%Y-%m-%d")
            
            pago_data = {
                "id_factura": factura_id,
                "importe": total,
                "metodo_pago": metodo_pago.lower(),  # El backend espera minúsculas
                "estado": "confirmado",  # Estado inicial del pago
                "fecha_pago": fecha_pago
            }
            
            res = self.api.create("pagos", pago_data)
            
            if res.get("success"):
                pago_creado = res.get("data", {})
                pago_id = pago_creado.get("id_pago") or pago_creado.get("id")
                
                messagebox.showinfo(
                    "Éxito",
                    f"Pago procesado correctamente.\n\n"
                    f"ID de Pago: {pago_id}\n"
                    f"Método: {metodo_pago.upper()}\n"
                    f"Importe: €{total:.2f}\n\n"
                    f"La factura ha sido marcada como PAGADA automáticamente."
                )
                
                if on_success_callback:
                    on_success_callback()
            else:
                error_msg = res.get("error", "Error desconocido")
                messagebox.showerror("Error", f"Error al procesar el pago:\n{error_msg}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar el pago:\n{str(e)}")

