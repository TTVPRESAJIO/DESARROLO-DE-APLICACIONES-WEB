# =====================================================================
#   ELECTRIC LIFE - app.py  (Semana 9)
#   Desarrollo de Aplicaciones Web · Proyecto Integrador U3
#
#   Aplicacion web con Flask.
#   - Configura la aplicacion y sus rutas principales.
#   - Renderiza las plantillas HTML de la carpeta templates/ con Jinja2.
#   - Los recursos (CSS, JS e imagenes) se sirven desde static/.
#
#   En esta etapa NO se usa base de datos: los datos son de ejemplo
#   (listas de diccionarios) para representar cada modulo del sistema.
#
#   Ejecucion local:
#       python app.py
#       Navegador: http://127.0.0.1:5000
# =====================================================================

from flask import Flask, render_template

# Instancia principal de la aplicacion Flask
app = Flask(__name__)


# =====================================================================
#   DATOS DE EJEMPLO (demostrativos, sin base de datos)
# =====================================================================

# ---- Modulo PRODUCTOS -------------------------------------------------
productos_data = [
    {"id": 1, "nombre": "Panel Solar 450W Monocristalino", "categoria": "Paneles",    "precio": 210.00, "stock": 24, "icono": "bi-grid-3x3-gap-fill"},
    {"id": 2, "nombre": "Batería de Litio 100Ah",          "categoria": "Baterías",   "precio": 480.00, "stock": 12, "icono": "bi-battery-charging"},
    {"id": 3, "nombre": "Inversor Híbrido 3kW",            "categoria": "Inversores", "precio": 395.00, "stock": 8,  "icono": "bi-cpu-fill"},
    {"id": 4, "nombre": "Kit Solar Router Anti-Apagón",    "categoria": "Kits",       "precio": 150.00, "stock": 30, "icono": "bi-wifi"},
    {"id": 5, "nombre": "Foco LED Solar 60W",              "categoria": "Iluminación","precio": 28.50,  "stock": 75, "icono": "bi-lightbulb-fill"},
    {"id": 6, "nombre": "Controlador de Carga MPPT 60A",   "categoria": "Inversores", "precio": 135.00, "stock": 0,  "icono": "bi-sliders"},
    {"id": 7, "nombre": "Cámara de Seguridad Solar",       "categoria": "Seguridad",  "precio": 89.90,  "stock": 18, "icono": "bi-camera-video-fill"},
    {"id": 8, "nombre": "Estructura de Montaje Techo",     "categoria": "Accesorios", "precio": 45.00,  "stock": 40, "icono": "bi-tools"},
]

# ---- Modulo CLIENTES --------------------------------------------------
clientes_data = [
    {"id": 1, "nombre": "María Fernanda Guevara", "cedula": "1600254789", "correo": "mf.guevara@gmail.com",   "telefono": "0987 112 233", "ciudad": "Puyo",     "estado": "Activo"},
    {"id": 2, "nombre": "Comercial El Sol S.A.",  "cedula": "1791234567001", "correo": "ventas@elsol.com.ec", "telefono": "032 887 445",  "ciudad": "Ambato",   "estado": "Activo"},
    {"id": 3, "nombre": "Luis Alberto Chimbo",    "cedula": "1600987654", "correo": "luis.chimbo@hotmail.com","telefono": "0995 774 118", "ciudad": "Tena",     "estado": "Activo"},
    {"id": 4, "nombre": "Panadería Doña Rosita",  "cedula": "1600445566001", "correo": "rositapan@gmail.com", "telefono": "0982 336 900", "ciudad": "Puyo",     "estado": "Inactivo"},
    {"id": 5, "nombre": "Andrea Salazar Vega",    "cedula": "1804556677", "correo": "andrea.svega@gmail.com", "telefono": "0961 220 874", "ciudad": "Riobamba", "estado": "Activo"},
]

# ---- Modulo PROVEEDORES -----------------------------------------------
proveedores_data = [
    {"id": 1, "empresa": "SolarTech Ecuador",   "contacto": "Ing. Pablo Naranjo", "correo": "ventas@solartech.ec",    "telefono": "022 456 780", "ciudad": "Quito",     "suministra": "Paneles solares"},
    {"id": 2, "empresa": "EnerLitio Import",    "contacto": "Lcda. Karla Ruiz",   "correo": "compras@enerlitio.com",  "telefono": "042 335 190", "ciudad": "Guayaquil", "suministra": "Baterías de litio"},
    {"id": 3, "empresa": "InverPower S.A.",     "contacto": "Ing. Diego Salas",   "correo": "info@inverpower.ec",     "telefono": "032 774 561", "ciudad": "Ambato",    "suministra": "Inversores y MPPT"},
    {"id": 4, "empresa": "LED Andina",          "contacto": "Sr. Marco Tapia",    "correo": "pedidos@ledandina.com",  "telefono": "022 998 340", "ciudad": "Quito",     "suministra": "Iluminación LED"},
]

# ---- Modulo FACTURACION -----------------------------------------------
facturas_data = [
    {"numero": "001-001-000125", "cliente": "María Fernanda Guevara", "fecha": "05/08/2026", "total": 690.00,  "estado": "Pagada"},
    {"numero": "001-001-000126", "cliente": "Comercial El Sol S.A.",  "fecha": "07/08/2026", "total": 1875.50, "estado": "Pagada"},
    {"numero": "001-001-000127", "cliente": "Luis Alberto Chimbo",    "fecha": "09/08/2026", "total": 240.00,  "estado": "Pendiente"},
    {"numero": "001-001-000128", "cliente": "Andrea Salazar Vega",    "fecha": "11/08/2026", "total": 528.90,  "estado": "Pendiente"},
    {"numero": "001-001-000129", "cliente": "Panadería Doña Rosita",  "fecha": "12/08/2026", "total": 150.00,  "estado": "Anulada"},
]


# =====================================================================
#   RUTAS DE LA APLICACION
#   Se definen con el decorador @app.route() y devuelven una plantilla
#   mediante render_template().
# =====================================================================

@app.route("/")
def index():
    """Pagina principal informativa del proyecto (landing)."""
    return render_template("index.html")


@app.route("/productos")
def productos():
    """Modulo de Productos: catalogo de equipos solares."""
    return render_template(
        "productos.html",
        productos=productos_data,
        total_productos=len(productos_data),
    )


@app.route("/clientes")
def clientes():
    """Modulo de Clientes: registro de clientes de Electric Life."""
    activos = [c for c in clientes_data if c["estado"] == "Activo"]
    return render_template(
        "clientes.html",
        clientes=clientes_data,
        total_clientes=len(clientes_data),
        total_activos=len(activos),
    )


@app.route("/proveedores")
def proveedores():
    """Modulo de Proveedores: empresas que abastecen el negocio."""
    return render_template(
        "proveedores.html",
        proveedores=proveedores_data,
        total_proveedores=len(proveedores_data),
    )


@app.route("/facturacion")
def facturacion():
    """Modulo de Facturacion: comprobantes emitidos."""
    # Solo se suman las facturas que no estan anuladas
    total_facturado = sum(f["total"] for f in facturas_data if f["estado"] != "Anulada")
    pendientes = [f for f in facturas_data if f["estado"] == "Pendiente"]
    return render_template(
        "facturacion.html",
        facturas=facturas_data,
        total_facturas=len(facturas_data),
        total_facturado=total_facturado,
        total_pendientes=len(pendientes),
    )


# =====================================================================
#   PUNTO DE ENTRADA
#   Ejecutar con:  python app.py   ->   http://127.0.0.1:5000
# =====================================================================
if __name__ == "__main__":
    app.run(debug=True)
