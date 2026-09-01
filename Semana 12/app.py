# ============================================================
#  ELECTRIC LIFE - Proyecto Integrador (Desarrollo de Aplicaciones Web)
#  Avance 12/16 - Semana 12: Persistencia de datos en un entorno local
#
#  Novedad de esta semana: los datos ya NO viven en listas de Python.
#  Ahora se guardan en una base de datos SQLite local
#  (data/electric_life.db) y sobreviven al cierre y reinicio de la app.
#
#  El flujo completo es:
#     Formulario -> Validacion (Flask-WTF) -> INSERT -> SELECT -> Jinja2
#
#  Se conserva TODO lo anterior: rutas, formularios, validadores, CSRF,
#  plantillas, componentes reutilizables y estilos.
# ============================================================
from flask import Flask, render_template, redirect, url_for, flash, abort, request

import db
from forms import (ProductoForm, ClienteForm, ProveedorForm, FacturaForm,
                   SolicitudForm, ContactoForm)

app = Flask(__name__)

# SECRET_KEY: la necesita Flask-WTF para firmar el token CSRF.
app.config["SECRET_KEY"] = "electric-life-clave-secreta-semana-12"

empresa = "Electric Life"

# Etiquetas legibles de las categorias de solicitud
ETIQUETAS_CATEGORIA = {
    "instalacion":   "Instalacion de sistema solar",
    "internet":      "Internet sin apagones",
    "mantenimiento": "Mantenimiento de un sistema existente",
    "asesoria":      "Asesoria y cotizacion",
}


# ============================================================
#  CATALOGO DE SERVICIOS
#  Es contenido informativo fijo de la portada (no son registros
#  que el usuario administre), por eso se mantiene en Python.
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


def o_404(registro):
    """Si la consulta no encontro el registro, responde 404."""
    if registro is None:
        abort(404)
    return registro


# ============================================================
#  PORTADA
# ============================================================
@app.route("/", methods=["GET", "POST"])
def index():
    form_solicitud = SolicitudForm()
    form_contacto = ContactoForm()
    cual = request.form.get("formulario")

    # Solo se guarda si el formulario supera TODAS las validaciones.
    if cual == "solicitud" and form_solicitud.validate_on_submit():
        numero = db.crear_solicitud(
            form_solicitud.sol_nombre.data.strip(),
            form_solicitud.sol_categoria.data,
            form_solicitud.sol_descripcion.data.strip())
        flash(f"Solicitud registrada correctamente. Tu numero de caso es el "
              f"#{numero}. Te contactaremos en 24 a 48 horas.", "success")
        return redirect(url_for("index") + "#solicitudes")

    if cual == "contacto" and form_contacto.validate_on_submit():
        db.crear_mensaje(
            form_contacto.con_nombre.data.strip(),
            form_contacto.con_correo.data.strip(),
            form_contacto.con_asunto.data,
            form_contacto.con_mensaje.data.strip())
        flash("Mensaje enviado. Respondemos en un plazo de 24 a 48 horas laborables.",
              "success")
        return redirect(url_for("index") + "#contacto")

    return render_template("index.html", titulo="Inicio", empresa=empresa,
                           servicios=SERVICIOS,
                           etiquetas=ETIQUETAS_CATEGORIA,
                           form_solicitud=form_solicitud,
                           form_contacto=form_contacto,
                           solicitudes=db.ultimas_solicitudes(6),
                           total_solicitudes=db.contar_solicitudes(),
                           total_productos=db.contar("productos"),
                           total_clientes=db.contar("clientes"),
                           total_proveedores=db.contar("proveedores"))


# ============================================================
#  MODULO PRODUCTOS  ·  flujo completo de persistencia
# ============================================================
@app.route("/productos")
def productos():
    """SELECT: los productos se leen de SQLite, no de una lista."""
    lista = db.listar_productos()
    return render_template("productos.html", titulo="Productos",
                           productos=lista, total=len(lista))


@app.route("/productos/nuevo", methods=["GET", "POST"])
def producto_nuevo():
    form = ProductoForm()

    # validate_on_submit() comprueba que sea POST, que el token CSRF sea
    # valido y que se cumplan todos los validadores de WTForms.
    if form.validate_on_submit():
        db.crear_producto(                       # <- INSERT parametrizado
            form.nombre.data.strip(),
            form.categoria.data,
            float(form.precio.data),
            form.stock.data,
            form.icono.data.strip() or "bi-box-seam")
        flash(f"Producto \"{form.nombre.data.strip()}\" guardado en la base de datos.",
              "success")
        return redirect(url_for("productos"))

    return render_template("formulario_producto.html", titulo="Nuevo producto",
                           form=form, modo="Registrar", accion=url_for("producto_nuevo"))


@app.route("/productos/editar/<int:id>", methods=["GET", "POST"])
def producto_editar(id):
    producto = o_404(db.obtener_producto(id))

    # data= rellena el formulario con lo que hay guardado en la base.
    form = ProductoForm(data=dict(producto))

    if form.validate_on_submit():
        db.actualizar_producto(id,
                               form.nombre.data.strip(),
                               form.categoria.data,
                               float(form.precio.data),
                               form.stock.data,
                               form.icono.data.strip() or "bi-box-seam")
        flash(f"Producto \"{form.nombre.data.strip()}\" actualizado.", "success")
        return redirect(url_for("productos"))

    return render_template("formulario_producto.html", titulo="Editar producto",
                           form=form, modo="Editar",
                           accion=url_for("producto_editar", id=id), registro=producto)


@app.route("/productos/eliminar/<int:id>", methods=["POST"])
def producto_eliminar(id):
    producto = o_404(db.obtener_producto(id))
    db.eliminar_producto(id)
    flash(f"Producto \"{producto['nombre']}\" eliminado de la base de datos.", "warning")
    return redirect(url_for("productos"))


# ============================================================
#  MODULO CLIENTES
# ============================================================
@app.route("/clientes")
def clientes():
    return render_template("clientes.html", titulo="Clientes",
                           clientes=db.listar_clientes(),
                           total_activos=db.contar_clientes_activos())


@app.route("/clientes/nuevo", methods=["GET", "POST"])
def cliente_nuevo():
    form = ClienteForm()

    if form.validate_on_submit():
        db.crear_cliente(form.nombre.data.strip(), form.cedula.data.strip(),
                         form.correo.data.strip(), form.telefono.data.strip(),
                         form.ciudad.data.strip(), form.estado.data)
        flash(f"Cliente \"{form.nombre.data.strip()}\" guardado en la base de datos.",
              "success")
        return redirect(url_for("clientes"))

    return render_template("formulario_cliente.html", titulo="Nuevo cliente",
                           form=form, modo="Registrar", accion=url_for("cliente_nuevo"))


@app.route("/clientes/editar/<int:id>", methods=["GET", "POST"])
def cliente_editar(id):
    cliente = o_404(db.obtener_cliente(id))
    form = ClienteForm(data=dict(cliente))

    if form.validate_on_submit():
        db.actualizar_cliente(id, form.nombre.data.strip(), form.cedula.data.strip(),
                              form.correo.data.strip(), form.telefono.data.strip(),
                              form.ciudad.data.strip(), form.estado.data)
        flash(f"Cliente \"{form.nombre.data.strip()}\" actualizado.", "success")
        return redirect(url_for("clientes"))

    return render_template("formulario_cliente.html", titulo="Editar cliente",
                           form=form, modo="Editar",
                           accion=url_for("cliente_editar", id=id), registro=cliente)


@app.route("/clientes/eliminar/<int:id>", methods=["POST"])
def cliente_eliminar(id):
    cliente = o_404(db.obtener_cliente(id))
    db.eliminar_cliente(id)
    flash(f"Cliente \"{cliente['nombre']}\" eliminado de la base de datos.", "warning")
    return redirect(url_for("clientes"))


# ============================================================
#  MODULO PROVEEDORES
# ============================================================
@app.route("/proveedores")
def proveedores():
    return render_template("proveedores.html", titulo="Proveedores",
                           proveedores=db.listar_proveedores())


@app.route("/proveedores/nuevo", methods=["GET", "POST"])
def proveedor_nuevo():
    form = ProveedorForm()

    if form.validate_on_submit():
        db.crear_proveedor(form.empresa.data.strip(), form.contacto.data.strip(),
                           form.correo.data.strip(), form.telefono.data.strip(),
                           form.ciudad.data.strip(), form.suministra.data.strip())
        flash(f"Proveedor \"{form.empresa.data.strip()}\" guardado en la base de datos.",
              "success")
        return redirect(url_for("proveedores"))

    return render_template("formulario_proveedor.html", titulo="Nuevo proveedor",
                           form=form, modo="Registrar", accion=url_for("proveedor_nuevo"))


@app.route("/proveedores/editar/<int:id>", methods=["GET", "POST"])
def proveedor_editar(id):
    proveedor = o_404(db.obtener_proveedor(id))
    form = ProveedorForm(data=dict(proveedor))

    if form.validate_on_submit():
        db.actualizar_proveedor(id, form.empresa.data.strip(), form.contacto.data.strip(),
                                form.correo.data.strip(), form.telefono.data.strip(),
                                form.ciudad.data.strip(), form.suministra.data.strip())
        flash(f"Proveedor \"{form.empresa.data.strip()}\" actualizado.", "success")
        return redirect(url_for("proveedores"))

    return render_template("formulario_proveedor.html", titulo="Editar proveedor",
                           form=form, modo="Editar",
                           accion=url_for("proveedor_editar", id=id), registro=proveedor)


@app.route("/proveedores/eliminar/<int:id>", methods=["POST"])
def proveedor_eliminar(id):
    proveedor = o_404(db.obtener_proveedor(id))
    db.eliminar_proveedor(id)
    flash(f"Proveedor \"{proveedor['empresa']}\" eliminado de la base de datos.", "warning")
    return redirect(url_for("proveedores"))


# ============================================================
#  MODULO FACTURACION
# ============================================================
@app.route("/facturacion")
def facturacion():
    return render_template("facturacion.html", titulo="Facturacion",
                           facturas=db.listar_facturas(),
                           total_facturado=db.total_facturado())


@app.route("/facturacion/nueva", methods=["GET", "POST"])
def factura_nueva():
    form = FacturaForm()

    if form.validate_on_submit():
        db.crear_factura(form.numero.data.strip(), form.cliente.data.strip(),
                         form.fecha.data, float(form.total.data), form.estado.data)
        flash(f"Factura {form.numero.data.strip()} guardada en la base de datos.",
              "success")
        return redirect(url_for("facturacion"))

    return render_template("formulario_facturacion.html", titulo="Nueva factura",
                           form=form, modo="Registrar", accion=url_for("factura_nueva"))


@app.route("/facturacion/editar/<int:id>", methods=["GET", "POST"])
def factura_editar(id):
    factura = o_404(db.obtener_factura(id))
    form = FacturaForm(data=dict(factura))

    if form.validate_on_submit():
        db.actualizar_factura(id, form.numero.data.strip(), form.cliente.data.strip(),
                              form.fecha.data, float(form.total.data), form.estado.data)
        flash(f"Factura {form.numero.data.strip()} actualizada.", "success")
        return redirect(url_for("facturacion"))

    return render_template("formulario_facturacion.html", titulo="Editar factura",
                           form=form, modo="Editar",
                           accion=url_for("factura_editar", id=id), registro=factura)


@app.route("/facturacion/eliminar/<int:id>", methods=["POST"])
def factura_eliminar(id):
    factura = o_404(db.obtener_factura(id))
    db.eliminar_factura(id)
    flash(f"Factura {factura['numero']} eliminada de la base de datos.", "warning")
    return redirect(url_for("facturacion"))


# ------------------------------------------------------------
#  Pagina de error amable
# ------------------------------------------------------------
@app.errorhandler(404)
def no_encontrado(e):
    return render_template("404.html", titulo="Pagina no encontrada"), 404


# ============================================================
#  ARRANQUE
#  Se preparan las tablas ANTES de levantar el servidor.
#  CREATE TABLE IF NOT EXISTS respeta lo que ya estaba guardado.
# ============================================================
if __name__ == "__main__":
    db.iniciar()
    app.run(debug=True)
