# ============================================================
#  ELECTRIC LIFE - Proyecto Integrador (Desarrollo de Aplicaciones Web)
#  Avance 10/16 - Semana 10: Plantillas, contenido dinamico y
#  reutilizacion de componentes con Flask + Jinja2.
#  En esta etapa NO se usa base de datos: los datos se definen
#  temporalmente en Python (listas y diccionarios).
# ============================================================
from flask import Flask, render_template

app = Flask(__name__)

# Variable simple enviada a las plantillas
empresa = "Electric Life"

# ----- Lista de diccionarios: PRODUCTOS -----
productos_data = [
    {"id": 1, "nombre": "Panel Solar Monocristalino 450W", "categoria": "Panel Solar", "precio": 180.00, "stock": 24, "icono": "bi-sun"},
    {"id": 2, "nombre": "Inversor Hibrido 3kW",            "categoria": "Inversor",    "precio": 650.00, "stock": 8,  "icono": "bi-lightning-charge"},
    {"id": 3, "nombre": "Bateria de Litio 100Ah",          "categoria": "Bateria",     "precio": 520.00, "stock": 12, "icono": "bi-battery-full"},
    {"id": 4, "nombre": "Regulador MPPT 60A",              "categoria": "Regulador",   "precio": 140.00, "stock": 15, "icono": "bi-sliders"},
    {"id": 5, "nombre": "Breaker DC 63A",                  "categoria": "Proteccion",  "precio": 25.00,  "stock": 40, "icono": "bi-shield-check"},
    {"id": 6, "nombre": "Cable Fotovoltaico 6mm (metro)",  "categoria": "Cableado",    "precio": 2.50,   "stock": 300,"icono": "bi-plug"},
    {"id": 7, "nombre": "Estructura de Montaje Aluminio",  "categoria": "Estructura",  "precio": 45.00,  "stock": 0,  "icono": "bi-grid-3x3"},
    {"id": 8, "nombre": "Controlador de Carga PWM 30A",    "categoria": "Regulador",   "precio": 60.00,  "stock": 0,  "icono": "bi-sliders"},
]

# ----- Lista de diccionarios: CLIENTES -----
clientes_data = [
    {"id": 1, "nombre": "Farmacia Su Salud",        "cedula": "1690012345001", "correo": "farmaciasusalud@gmail.com",  "telefono": "032885001", "ciudad": "Puyo", "estado": "Activo"},
    {"id": 2, "nombre": "Ferreteria El Constructor","cedula": "1690023456001", "correo": "elconstructor@gmail.com",     "telefono": "032885002", "ciudad": "Puyo", "estado": "Activo"},
    {"id": 3, "nombre": "Restaurante El Jardin",    "cedula": "1690034567001", "correo": "eljardinpuyo@gmail.com",      "telefono": "032885003", "ciudad": "Puyo", "estado": "Inactivo"},
    {"id": 4, "nombre": "Juan Andres Perez",        "cedula": "1600456789",    "correo": "juanperez@gmail.com",        "telefono": "0991112233","ciudad": "Puyo", "estado": "Activo"},
    {"id": 5, "nombre": "Cyber Amazonia",           "cedula": "1690045678001", "correo": "cyberamazonia@gmail.com",     "telefono": "032885004", "ciudad": "Puyo", "estado": "Activo"},
]

# ----- Lista de diccionarios: PROVEEDORES -----
proveedores_data = [
    {"id": 1, "empresa": "Proviento",       "contacto": "Ventas Proviento", "correo": "ventas@proviento.com.ec", "telefono": "022500000", "ciudad": "Quito",   "suministra": "Paneles, inversores y baterias"},
    {"id": 2, "empresa": "Pintulac",        "contacto": "Atencion Cliente", "correo": "info@pintulac.com.ec",    "telefono": "1800746852","ciudad": "Nacional","suministra": "Paneles, inversores y baterias"},
    {"id": 3, "empresa": "Sunny Future",    "contacto": "Ventas SF",        "correo": "info@sunnyfuture.co",     "telefono": "022600000", "ciudad": "Quito",   "suministra": "Baterias de litio e inversores"},
    {"id": 4, "empresa": "Amawtec",         "contacto": "Distribucion",     "correo": "ventas@amawtec.com",      "telefono": "062600000", "ciudad": "Ibarra",  "suministra": "Kits fotovoltaicos Growatt"},
]

# ----- Lista de diccionarios: FACTURAS -----
facturas_data = [
    {"numero": "001-001-000001", "cliente": "Farmacia Su Salud",         "fecha": "2026-07-12", "total": 2730.00, "estado": "Pagada"},
    {"numero": "001-001-000002", "cliente": "Cyber Amazonia",            "fecha": "2026-07-23", "total": 1530.00, "estado": "Pagada"},
    {"numero": "001-001-000003", "cliente": "Ferreteria El Constructor", "fecha": "2026-07-28", "total": 890.00,  "estado": "Pendiente"},
    {"numero": "001-001-000004", "cliente": "Juan Andres Perez",         "fecha": "2026-08-02", "total": 420.00,  "estado": "Pendiente"},
    {"numero": "001-001-000005", "cliente": "Restaurante El Jardin",     "fecha": "2026-08-05", "total": 310.00,  "estado": "Anulada"},
]


@app.route("/")
def index():
    return render_template("index.html", titulo="Inicio", empresa=empresa,
                           total_productos=len(productos_data),
                           total_clientes=len(clientes_data),
                           total_proveedores=len(proveedores_data))


@app.route("/productos")
def productos():
    return render_template("productos.html", titulo="Productos",
                           productos=productos_data, total=len(productos_data))


@app.route("/clientes")
def clientes():
    # Calculo hecho en Python (backend): clientes activos
    activos = [c for c in clientes_data if c["estado"] == "Activo"]
    return render_template("clientes.html", titulo="Clientes",
                           clientes=clientes_data, total_activos=len(activos))


@app.route("/proveedores")
def proveedores():
    return render_template("proveedores.html", titulo="Proveedores",
                           proveedores=proveedores_data)


@app.route("/facturacion")
def facturacion():
    # El total ignora las facturas anuladas (calculo en el backend)
    total_facturado = sum(f["total"] for f in facturas_data if f["estado"] != "Anulada")
    return render_template("facturacion.html", titulo="Facturacion",
                           facturas=facturas_data, total_facturado=total_facturado)


if __name__ == "__main__":
    app.run(debug=True)
