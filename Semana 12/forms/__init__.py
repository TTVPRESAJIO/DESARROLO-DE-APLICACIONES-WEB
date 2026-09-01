# =====================================================================
#  ELECTRIC LIFE · paquete "forms"  (Semana 11)
#  ---------------------------------------------------------------------
#  Aqui viven las clases de formulario del proyecto, una por modulo.
#  Separarlas de app.py mantiene el proyecto ordenado y permite que la
#  MISMA clase se reutilice para registrar y para editar un registro.
#
#  Este archivo reexporta las clases para poder importarlas asi:
#       from forms import ProductoForm, ClienteForm
# =====================================================================

from .producto_form import ProductoForm
from .cliente_form import ClienteForm
from .proveedor_form import ProveedorForm
from .facturacion_form import FacturaForm
from .portada_form import SolicitudForm, ContactoForm

__all__ = [
    "ProductoForm",
    "ClienteForm",
    "ProveedorForm",
    "FacturaForm",
    "SolicitudForm",
    "ContactoForm",
]
