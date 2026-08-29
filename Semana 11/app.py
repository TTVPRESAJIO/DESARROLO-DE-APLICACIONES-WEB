# ============================================================
#  ELECTRIC LIFE - Proyecto Integrador (Desarrollo de Aplicaciones Web)
#  Avance 11/16 - Semana 11: Validacion de formularios con
#  Flask-WTF y WTForms.
#
#  Se conserva todo lo anterior (rutas, plantillas, contenido
#  dinamico y componentes) y se anaden formularios con:
#    · Clases que heredan de FlaskForm, organizadas en forms/
#    · Validadores (DataRequired, Length, Email, NumberRange, Regexp)
#    · Rutas que aceptan GET y POST
#    · form.validate_on_submit() antes de procesar
#    · Proteccion CSRF mediante SECRET_KEY + form.hidden_tag()
#
#  En esta etapa NO se usa base de datos: los datos se mantienen en
#  estructuras de Python durante la ejecucion de la aplicacion.
# ============================================================
from datetime import date, datetime

from flask import Flask, render_template, redirect, url_for, flash, abort, request

from forms import (ProductoForm, ClienteForm, ProveedorForm, FacturaForm,
                   SolicitudForm, ContactoForm)

app = Flask(__name__)

# ------------------------------------------------------------
#  SECRET_KEY: la necesita Flask-WTF para firmar el token CSRF
#  que protege los formularios. Sin ella, form.hidden_tag() no
#  puede generar el token y los envios serian rechazados.
# ------------------------------------------------------------
app.config["SECRET_KEY"] = "electric-life-clave-secreta-semana-11"

# Variable simple enviada a las plantillas
empresa = "Electric Life"


# ============================================================
#  DATOS EN MEMORIA (sin base de datos, como pide la actividad)
#  Se modifican al registrar, editar o eliminar mientras la
#  aplicacion esta en ejecucion.
# ============================================================
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

clientes_data = [
    {"id": 1, "nombre": "Farmacia Su Salud",         "cedula": "1690012345001", "correo": "farmaciasusalud@gmail.com", "telefono": "032885001", "ciudad": "Puyo", "estado": "Activo"},
    {"id": 2, "nombre": "Ferreteria El Constructor", "cedula": "1690023456001", "correo": "elconstructor@gmail.com",   "telefono": "032885002", "ciudad": "Puyo", "estado": "Activo"},
    {"id": 3, "nombre": "Restaurante El Jardin",     "cedula": "1690034567001", "correo": "eljardinpuyo@gmail.com",    "telefono": "032885003", "ciudad": "Puyo", "estado": "Inactivo"},
    {"id": 4, "nombre": "Juan Andres Perez",         "cedula": "1600456789",    "correo": "juanperez@gmail.com",       "telefono": "0991112233","ciudad": "Puyo", "estado": "Activo"},
    {"id": 5, "nombre": "Cyber Amazonia",            "cedula": "1690045678001", "correo": "cyberamazonia@gmail.com",   "telefono": "032885004", "ciudad": "Puyo", "estado": "Activo"},
]

proveedores_data = [
    {"id": 1, "empresa": "Proviento",    "contacto": "Ventas Proviento", "correo": "ventas@proviento.com.ec", "telefono": "022500000", "ciudad": "Quito",   "suministra": "Paneles, inversores y baterias"},
    {"id": 2, "empresa": "Pintulac",     "contacto": "Atencion Cliente", "correo": "info@pintulac.com.ec",    "telefono": "1800746852","ciudad": "Nacional","suministra": "Paneles, inversores y baterias"},
    {"id": 3, "empresa": "Sunny Future", "contacto": "Ventas SF",        "correo": "info@sunnyfuture.co",     "telefono": "022600000", "ciudad": "Quito",   "suministra": "Baterias de litio e inversores"},
    {"id": 4, "empresa": "Amawtec",      "contacto": "Distribucion",     "correo": "ventas@amawtec.com",      "telefono": "062600000", "ciudad": "Ibarra",  "suministra": "Kits fotovoltaicos Growatt"},
]

facturas_data = [
    {"id": 1, "numero": "001-001-000001", "cliente": "Farmacia Su Salud",         "fecha": date(2026, 7, 12), "total": 2730.00, "estado": "Pagada"},
    {"id": 2, "numero": "001-001-000002", "cliente": "Cyber Amazonia",            "fecha": date(2026, 7, 23), "total": 1530.00, "estado": "Pagada"},
    {"id": 3, "numero": "001-001-000003", "cliente": "Ferreteria El Constructor", "fecha": date(2026, 7, 28), "total": 890.00,  "estado": "Pendiente"},
    {"id": 4, "numero": "001-001-000004", "cliente": "Juan Andres Perez",         "fecha": date(2026, 8, 2),  "total": 420.00,  "estado": "Pendiente"},
    {"id": 5, "numero": "001-001-000005", "cliente": "Restaurante El Jardin",     "fecha": date(2026, 8, 5),  "total": 310.00,  "estado": "Anulada"},
]


# ------------------------------------------------------------
#  Solicitudes y mensajes recibidos desde la portada.
#  Se guardan en memoria mientras la aplicacion esta en ejecucion
#  (esta semana todavia no se usa base de datos).
# ------------------------------------------------------------
solicitudes_data = []
mensajes_data = []

# Etiquetas legibles de las categorias, para mostrarlas en el listado
ETIQUETAS_CATEGORIA = {
    "instalacion":   "Instalacion de sistema solar",
    "internet":      "Internet sin apagones",
    "mantenimiento": "Mantenimiento de un sistema existente",
    "asesoria":      "Asesoria y cotizacion",
}


# ============================================================
#  CATALOGO UNICO DE SERVICIOS
#  Se envia a la plantilla y de ahi a JavaScript, que genera las
#  tarjetas y la tabla comparativa de la portada. Al haber una
#  sola fuente, la vista de tarjetas y la de tabla no se pueden
#  desincronizar.
# ============================================================
SERVICIOS = [
    {"icono": "bi-box-seam-fill", "titulo": "Venta de Sistemas Solares", "categoria": "instalacion",
     "texto": "Kits completos de respaldo solar para todo tipo de consumo.",
     "detalle": "Ofrecemos kits solares dimensionados segun tu consumo: panel, inversor, bateria de litio y accesorios. Incluye garantia y asesoria de instalacion."},
    {"icono": "bi-hammer", "titulo": "Instalacion Profesional", "categoria": "instalacion",
     "texto": "Montaje de paneles solares con personal tecnico certificado.",
     "detalle": "Nuestro equipo certificado realiza el montaje, cableado y puesta en marcha del sistema, cumpliendo normas de seguridad electrica."},
    {"icono": "bi-wifi", "titulo": "Internet sin Apagones", "categoria": "internet",
     "texto": "Manten tu router activo durante cortes de luz con nuestros sistemas.",
     "detalle": "Sistema de respaldo dedicado para tu router y ONT. Mantiene tu internet y teletrabajo activos hasta 8 horas durante un apagon."},
    {"icono": "bi-lightbulb-fill", "titulo": "Iluminacion LED", "categoria": "instalacion",
     "texto": "Soluciones de iluminacion de emergencia de bajo consumo.",
     "detalle": "Focos y tiras LED de bajo consumo con activacion automatica ante cortes de energia. Ideales para hogar y negocio."},
    {"icono": "bi-camera-video-fill", "titulo": "Camaras de Seguridad", "categoria": "instalacion",
     "texto": "Respaldo energetico para tus camaras de vigilancia 24/7.",
     "detalle": "Respaldo energetico para tu sistema de videovigilancia (DVR/NVR y camaras), garantizando monitoreo continuo dia y noche."},
    {"icono": "bi-wrench-adjustable-circle-fill", "titulo": "Mantenimiento", "categoria": "mantenimiento",
     "texto": "Mantenimiento preventivo y correctivo para todos nuestros sistemas.",
     "detalle": "Planes de mantenimiento preventivo y correctivo: limpieza de paneles, revision de baterias y diagnostico de rendimiento."},
    {"icono": "bi-graph-up-arrow", "titulo": "Optimizacion Energetica", "categoria": "asesoria",
     "texto": "Evaluamos tu consumo y disenamos la solucion mas eficiente.",
     "detalle": "Analizamos tu consumo electrico y proponemos la configuracion mas eficiente para reducir costos y maximizar el respaldo."},
    {"icono": "bi-chat-dots-fill", "titulo": "Asesoria Personalizada", "categoria": "asesoria",
     "texto": "Te guiamos para elegir el sistema ideal segun tu presupuesto.",
     "detalle": "Asesoria gratuita para elegir el sistema ideal segun tu presupuesto y necesidades. Sin compromiso."},
]


# ============================================================
#  UTILIDADES
# ============================================================
def siguiente_id(coleccion):
    """Devuelve el id siguiente de una lista de diccionarios."""
    return max((item["id"] for item in coleccion), default=0) + 1


def buscar(coleccion, id_buscado):
    """Busca un registro por id. Si no existe, responde 404."""
    for item in coleccion:
        if item["id"] == id_buscado:
            return item
    abort(404)


# ============================================================
#  RUTAS DE CONSULTA (las de la Semana 10, se conservan)
# ============================================================
@app.route("/", methods=["GET", "POST"])
def index():
    """Portada informativa. Tambien recibe los dos formularios publicos.

    Los dos formularios conviven en la misma pagina, por eso cada uno
    lleva un campo oculto "formulario" que indica cual se envio.
    """
    form_solicitud = SolicitudForm()
    form_contacto = ContactoForm()
    cual = request.form.get("formulario")

    # --- Solicitud de servicio ---
    if cual == "solicitud" and form_solicitud.validate_on_submit():
        solicitudes_data.insert(0, {
            "id": len(solicitudes_data) + 1,
            "nombre": form_solicitud.sol_nombre.data.strip(),
            "categoria": form_solicitud.sol_categoria.data,
            "descripcion": form_solicitud.sol_descripcion.data.strip(),
            "fecha": datetime.now(),
        })
        flash(f"Solicitud registrada correctamente. Tu numero de caso es el "
              f"#{len(solicitudes_data)}. Te contactaremos en 24 a 48 horas.", "success")
        return redirect(url_for("index") + "#solicitudes")

    # --- Mensaje de contacto ---
    if cual == "contacto" and form_contacto.validate_on_submit():
        mensajes_data.append({
            "nombre": form_contacto.con_nombre.data.strip(),
            "correo": form_contacto.con_correo.data.strip(),
            "asunto": form_contacto.con_asunto.data,
            "mensaje": form_contacto.con_mensaje.data.strip(),
            "fecha": datetime.now(),
        })
        flash("Mensaje enviado. Respondemos en un plazo de 24 a 48 horas laborables.",
              "success")
        return redirect(url_for("index") + "#contacto")

    return render_template("index.html", titulo="Inicio", empresa=empresa,
                           servicios=SERVICIOS,
                           etiquetas=ETIQUETAS_CATEGORIA,
                           form_solicitud=form_solicitud,
                           form_contacto=form_contacto,
                           solicitudes=solicitudes_data[:6],
                           total_solicitudes=len(solicitudes_data),
                           total_productos=len(productos_data),
                           total_clientes=len(clientes_data),
                           total_proveedores=len(proveedores_data))


@app.route("/productos")
def productos():
    return render_template("productos.html", titulo="Productos",
                           productos=productos_data, total=len(productos_data))


@app.route("/clientes")
def clientes():
    activos = [c for c in clientes_data if c["estado"] == "Activo"]
    return render_template("clientes.html", titulo="Clientes",
                           clientes=clientes_data, total_activos=len(activos))


@app.route("/proveedores")
def proveedores():
    return render_template("proveedores.html", titulo="Proveedores",
                           proveedores=proveedores_data)


@app.route("/facturacion")
def facturacion():
    total_facturado = sum(f["total"] for f in facturas_data if f["estado"] != "Anulada")
    return render_template("facturacion.html", titulo="Facturacion",
                           facturas=facturas_data, total_facturado=total_facturado)


# ============================================================
#  MODULO PRODUCTOS · registrar y editar
#  La MISMA clase ProductoForm sirve para las dos operaciones.
# ============================================================
@app.route("/productos/nuevo", methods=["GET", "POST"])
def producto_nuevo():
    form = ProductoForm()

    # validate_on_submit() devuelve True solo si:
    #   1) la peticion es POST, y
    #   2) el token CSRF es valido, y
    #   3) TODOS los validadores se cumplen.
    if form.validate_on_submit():
        productos_data.append({
            "id": siguiente_id(productos_data),
            "nombre": form.nombre.data.strip(),
            "categoria": form.categoria.data,
            "precio": float(form.precio.data),
            "stock": form.stock.data,
            "icono": form.icono.data.strip() or "bi-box-seam",
        })
        flash(f"Producto \"{form.nombre.data.strip()}\" registrado correctamente.", "success")
        return redirect(url_for("productos"))

    return render_template("formulario_producto.html", titulo="Nuevo producto",
                           form=form, modo="Registrar", accion=url_for("producto_nuevo"))


@app.route("/productos/editar/<int:id>", methods=["GET", "POST"])
def producto_editar(id):
    producto = buscar(productos_data, id)

    # data= rellena el formulario con los valores actuales del registro.
    form = ProductoForm(data=producto)

    if form.validate_on_submit():
        producto["nombre"] = form.nombre.data.strip()
        producto["categoria"] = form.categoria.data
        producto["precio"] = float(form.precio.data)
        producto["stock"] = form.stock.data
        producto["icono"] = form.icono.data.strip() or "bi-box-seam"
        flash(f"Producto \"{producto['nombre']}\" actualizado correctamente.", "success")
        return redirect(url_for("productos"))

    return render_template("formulario_producto.html", titulo="Editar producto",
                           form=form, modo="Editar",
                           accion=url_for("producto_editar", id=id), registro=producto)


@app.route("/productos/eliminar/<int:id>", methods=["POST"])
def producto_eliminar(id):
    producto = buscar(productos_data, id)
    productos_data.remove(producto)
    flash(f"Producto \"{producto['nombre']}\" eliminado.", "warning")
    return redirect(url_for("productos"))


# ============================================================
#  MODULO CLIENTES · registrar y editar
# ============================================================
@app.route("/clientes/nuevo", methods=["GET", "POST"])
def cliente_nuevo():
    form = ClienteForm()

    if form.validate_on_submit():
        clientes_data.append({
            "id": siguiente_id(clientes_data),
            "nombre": form.nombre.data.strip(),
            "cedula": form.cedula.data.strip(),
            "correo": form.correo.data.strip(),
            "telefono": form.telefono.data.strip(),
            "ciudad": form.ciudad.data.strip(),
            "estado": form.estado.data,
        })
        flash(f"Cliente \"{form.nombre.data.strip()}\" registrado correctamente.", "success")
        return redirect(url_for("clientes"))

    return render_template("formulario_cliente.html", titulo="Nuevo cliente",
                           form=form, modo="Registrar", accion=url_for("cliente_nuevo"))


@app.route("/clientes/editar/<int:id>", methods=["GET", "POST"])
def cliente_editar(id):
    cliente = buscar(clientes_data, id)
    form = ClienteForm(data=cliente)

    if form.validate_on_submit():
        cliente["nombre"] = form.nombre.data.strip()
        cliente["cedula"] = form.cedula.data.strip()
        cliente["correo"] = form.correo.data.strip()
        cliente["telefono"] = form.telefono.data.strip()
        cliente["ciudad"] = form.ciudad.data.strip()
        cliente["estado"] = form.estado.data
        flash(f"Cliente \"{cliente['nombre']}\" actualizado correctamente.", "success")
        return redirect(url_for("clientes"))

    return render_template("formulario_cliente.html", titulo="Editar cliente",
                           form=form, modo="Editar",
                           accion=url_for("cliente_editar", id=id), registro=cliente)


@app.route("/clientes/eliminar/<int:id>", methods=["POST"])
def cliente_eliminar(id):
    cliente = buscar(clientes_data, id)
    clientes_data.remove(cliente)
    flash(f"Cliente \"{cliente['nombre']}\" eliminado.", "warning")
    return redirect(url_for("clientes"))


# ============================================================
#  MODULO PROVEEDORES · registrar y editar
# ============================================================
@app.route("/proveedores/nuevo", methods=["GET", "POST"])
def proveedor_nuevo():
    form = ProveedorForm()

    if form.validate_on_submit():
        proveedores_data.append({
            "id": siguiente_id(proveedores_data),
            "empresa": form.empresa.data.strip(),
            "contacto": form.contacto.data.strip(),
            "correo": form.correo.data.strip(),
            "telefono": form.telefono.data.strip(),
            "ciudad": form.ciudad.data.strip(),
            "suministra": form.suministra.data.strip(),
        })
        flash(f"Proveedor \"{form.empresa.data.strip()}\" registrado correctamente.", "success")
        return redirect(url_for("proveedores"))

    return render_template("formulario_proveedor.html", titulo="Nuevo proveedor",
                           form=form, modo="Registrar", accion=url_for("proveedor_nuevo"))


@app.route("/proveedores/editar/<int:id>", methods=["GET", "POST"])
def proveedor_editar(id):
    proveedor = buscar(proveedores_data, id)
    form = ProveedorForm(data=proveedor)

    if form.validate_on_submit():
        proveedor["empresa"] = form.empresa.data.strip()
        proveedor["contacto"] = form.contacto.data.strip()
        proveedor["correo"] = form.correo.data.strip()
        proveedor["telefono"] = form.telefono.data.strip()
        proveedor["ciudad"] = form.ciudad.data.strip()
        proveedor["suministra"] = form.suministra.data.strip()
        flash(f"Proveedor \"{proveedor['empresa']}\" actualizado correctamente.", "success")
        return redirect(url_for("proveedores"))

    return render_template("formulario_proveedor.html", titulo="Editar proveedor",
                           form=form, modo="Editar",
                           accion=url_for("proveedor_editar", id=id), registro=proveedor)


@app.route("/proveedores/eliminar/<int:id>", methods=["POST"])
def proveedor_eliminar(id):
    proveedor = buscar(proveedores_data, id)
    proveedores_data.remove(proveedor)
    flash(f"Proveedor \"{proveedor['empresa']}\" eliminado.", "warning")
    return redirect(url_for("proveedores"))


# ============================================================
#  MODULO FACTURACION · registrar y editar
# ============================================================
@app.route("/facturacion/nueva", methods=["GET", "POST"])
def factura_nueva():
    form = FacturaForm()

    if form.validate_on_submit():
        facturas_data.append({
            "id": siguiente_id(facturas_data),
            "numero": form.numero.data.strip(),
            "cliente": form.cliente.data.strip(),
            "fecha": form.fecha.data,
            "total": float(form.total.data),
            "estado": form.estado.data,
        })
        flash(f"Factura {form.numero.data.strip()} registrada correctamente.", "success")
        return redirect(url_for("facturacion"))

    return render_template("formulario_facturacion.html", titulo="Nueva factura",
                           form=form, modo="Registrar", accion=url_for("factura_nueva"))


@app.route("/facturacion/editar/<int:id>", methods=["GET", "POST"])
def factura_editar(id):
    factura = buscar(facturas_data, id)
    form = FacturaForm(data=factura)

    if form.validate_on_submit():
        factura["numero"] = form.numero.data.strip()
        factura["cliente"] = form.cliente.data.strip()
        factura["fecha"] = form.fecha.data
        factura["total"] = float(form.total.data)
        factura["estado"] = form.estado.data
        flash(f"Factura {factura['numero']} actualizada correctamente.", "success")
        return redirect(url_for("facturacion"))

    return render_template("formulario_facturacion.html", titulo="Editar factura",
                           form=form, modo="Editar",
                           accion=url_for("factura_editar", id=id), registro=factura)


@app.route("/facturacion/eliminar/<int:id>", methods=["POST"])
def factura_eliminar(id):
    factura = buscar(facturas_data, id)
    facturas_data.remove(factura)
    flash(f"Factura {factura['numero']} eliminada.", "warning")
    return redirect(url_for("facturacion"))


# ------------------------------------------------------------
#  Pagina de error amable.
#  [N9] El mensaje se expresa en lenguaje llano, explica el
#  problema y ofrece una salida.
# ------------------------------------------------------------
@app.errorhandler(404)
def no_encontrado(e):
    return render_template("404.html", titulo="Pagina no encontrada"), 404


if __name__ == "__main__":
    app.run(debug=True)
