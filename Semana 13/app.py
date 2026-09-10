# ============================================================
#  ELECTRIC LIFE - Proyecto Integrador (Desarrollo de Aplicaciones Web)
#  Avance 13/16 - Semana 13: Uso de bases de datos relacionales
#
#  La aplicacion pasa de SQLite (Semana 12) a una base de datos
#  relacional MySQL / MariaDB.
#
#  Novedades de esta semana:
#    · Conexion centralizada en conexion/conexion.py
#    · Modelo relacional con claves primarias y FORANEAS
#         productos.id_proveedor -> proveedores.id_proveedor
#         facturas.id_cliente    -> clientes.id_cliente
#    · Flujo completo SELECT / INSERT / UPDATE / DELETE sobre MySQL
#    · Consultas relacionadas con JOIN entre dos tablas
#
#  Se conserva TODO lo anterior: formularios Flask-WTF, validadores,
#  SECRET_KEY, CSRF, plantillas, componentes reutilizables y estilos.
# ============================================================
import os

from flask import Flask, render_template, redirect, url_for, flash, abort, request

import datos
from forms import (ProductoForm, ClienteForm, ProveedorForm, FacturaForm,
                   SolicitudForm, ContactoForm)

app = Flask(__name__)

# SECRET_KEY: la necesita Flask-WTF para firmar el token CSRF.
app.config["SECRET_KEY"] = "electric-life-clave-secreta-semana-13"

# ------------------------------------------------------------
#  Configuracion de la base de datos relacional.
#  Se leen de variables de entorno para no dejar contrasenas
#  reales escritas en el repositorio. Los valores por defecto
#  corresponden a XAMPP recien instalado (root sin contrasena).
# ------------------------------------------------------------
app.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST", "localhost")
app.config["MYSQL_USER"] = os.environ.get("MYSQL_USER", "root")
app.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD", "")
app.config["MYSQL_DATABASE"] = os.environ.get("MYSQL_DATABASE", "electric_life_web")
app.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT", 3306))

empresa = "Electric Life"

ETIQUETAS_CATEGORIA = {
    "instalacion":   "Instalacion de sistema solar",
    "internet":      "Internet sin apagones",
    "mantenimiento": "Mantenimiento de un sistema existente",
    "asesoria":      "Asesoria y cotizacion",
}


# ============================================================
#  CATALOGO DE SERVICIOS (contenido informativo de la portada)
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
    if registro is None:
        abort(404)
    return registro


def cargar_proveedores(form):
    """Rellena el desplegable de proveedores desde la base de datos."""
    form.id_proveedor.choices = [(0, "— Sin proveedor asignado —")] + [
        (id_prov, empresa) for id_prov, empresa in datos.opciones_proveedores()
    ]


def cargar_clientes(form):
    """Rellena el desplegable de clientes desde la base de datos."""
    form.id_cliente.choices = [(0, "Selecciona un cliente...")] + [
        (id_cli, nombre) for id_cli, nombre in datos.opciones_clientes()
    ]


# ============================================================
#  COMPROBACION DE LA CONEXION
#  Ruta sugerida en el material de clase: muestra las tablas
#  existentes para confirmar que Flask llega a la base.
# ============================================================
@app.route("/test_db")
def test_db():
    try:
        tablas = datos.probar_conexion()
        return render_template("test_db.html", titulo="Conexion", tablas=tablas,
                               base=app.config["MYSQL_DATABASE"],
                               host=app.config["MYSQL_HOST"], error=None)
    except Exception as e:
        return render_template("test_db.html", titulo="Conexion", tablas=[],
                               base=app.config["MYSQL_DATABASE"],
                               host=app.config["MYSQL_HOST"], error=str(e)), 500


# ============================================================
#  PORTADA
# ============================================================
@app.route("/", methods=["GET", "POST"])
def index():
    form_solicitud = SolicitudForm()
    form_contacto = ContactoForm()
    cual = request.form.get("formulario")

    if cual == "solicitud" and form_solicitud.validate_on_submit():
        numero = datos.crear_solicitud(
            form_solicitud.sol_nombre.data.strip(),
            form_solicitud.sol_categoria.data,
            form_solicitud.sol_descripcion.data.strip())
        flash(f"Solicitud registrada correctamente. Tu numero de caso es el "
              f"#{numero}. Te contactaremos en 24 a 48 horas.", "success")
        return redirect(url_for("index") + "#solicitudes")

    if cual == "contacto" and form_contacto.validate_on_submit():
        datos.crear_mensaje(
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
                           solicitudes=datos.ultimas_solicitudes(6),
                           total_solicitudes=datos.contar_solicitudes(),
                           total_productos=datos.contar("productos"),
                           total_clientes=datos.contar("clientes"),
                           total_proveedores=datos.contar("proveedores"))


# ============================================================
#  MODULO PRODUCTOS
#  Es el modulo con el flujo completo sobre MySQL:
#      LISTAR (SELECT + JOIN) · AGREGAR (INSERT)
#      MODIFICAR (UPDATE ... WHERE) · ELIMINAR (DELETE ... WHERE)
# ============================================================
@app.route("/productos")
def productos():
    """LISTAR · SELECT con JOIN hacia proveedores."""
    lista = datos.listar_productos()
    return render_template("productos.html", titulo="Productos",
                           productos=lista, total=len(lista))


@app.route("/productos/nuevo", methods=["GET", "POST"])
def producto_nuevo():
    """AGREGAR · INSERT INTO tras validar con Flask-WTF."""
    form = ProductoForm()
    cargar_proveedores(form)

    if form.validate_on_submit():
        datos.crear_producto(
            form.nombre.data.strip(),
            form.categoria.data,
            float(form.precio.data),
            form.stock.data,
            form.icono.data.strip() or "bi-box-seam",
            form.id_proveedor.data or None)      # 0 -> NULL en la columna FK
        flash(f"Producto \"{form.nombre.data.strip()}\" agregado a la base de datos.",
              "success")
        return redirect(url_for("productos"))

    return render_template("formulario_producto.html", titulo="Nuevo producto",
                           form=form, modo="Registrar", accion=url_for("producto_nuevo"))


@app.route("/productos/editar/<int:id>", methods=["GET", "POST"])
def producto_editar(id):
    """MODIFICAR · se recupera el registro y se guarda con UPDATE ... WHERE."""
    producto = o_404(datos.obtener_producto(id))

    form = ProductoForm(data=producto)
    cargar_proveedores(form)

    if form.validate_on_submit():
        datos.actualizar_producto(id,
                                  form.nombre.data.strip(),
                                  form.categoria.data,
                                  float(form.precio.data),
                                  form.stock.data,
                                  form.icono.data.strip() or "bi-box-seam",
                                  form.id_proveedor.data or None)
        flash(f"Producto \"{form.nombre.data.strip()}\" modificado en la base de datos.",
              "success")
        return redirect(url_for("productos"))

    return render_template("formulario_producto.html", titulo="Editar producto",
                           form=form, modo="Editar",
                           accion=url_for("producto_editar", id=id), registro=producto)


@app.route("/productos/eliminar/<int:id>", methods=["POST"])
def producto_eliminar(id):
    """ELIMINAR · DELETE FROM ... WHERE solo el registro indicado."""
    producto = o_404(datos.obtener_producto(id))
    datos.eliminar_producto(id)
    flash(f"Producto \"{producto['nombre']}\" eliminado de la base de datos.", "warning")
    return redirect(url_for("productos"))


# ============================================================
#  MODULO CLIENTES
# ============================================================
@app.route("/clientes")
def clientes():
    return render_template("clientes.html", titulo="Clientes",
                           clientes=datos.listar_clientes(),
                           total_activos=datos.contar_clientes_activos())


@app.route("/clientes/nuevo", methods=["GET", "POST"])
def cliente_nuevo():
    form = ClienteForm()

    if form.validate_on_submit():
        datos.crear_cliente(form.nombre.data.strip(), form.cedula.data.strip(),
                            form.correo.data.strip(), form.telefono.data.strip(),
                            form.ciudad.data.strip(), form.estado.data)
        flash(f"Cliente \"{form.nombre.data.strip()}\" agregado a la base de datos.",
              "success")
        return redirect(url_for("clientes"))

    return render_template("formulario_cliente.html", titulo="Nuevo cliente",
                           form=form, modo="Registrar", accion=url_for("cliente_nuevo"))


@app.route("/clientes/editar/<int:id>", methods=["GET", "POST"])
def cliente_editar(id):
    cliente = o_404(datos.obtener_cliente(id))
    form = ClienteForm(data=cliente)

    if form.validate_on_submit():
        datos.actualizar_cliente(id, form.nombre.data.strip(), form.cedula.data.strip(),
                                 form.correo.data.strip(), form.telefono.data.strip(),
                                 form.ciudad.data.strip(), form.estado.data)
        flash(f"Cliente \"{form.nombre.data.strip()}\" modificado.", "success")
        return redirect(url_for("clientes"))

    return render_template("formulario_cliente.html", titulo="Editar cliente",
                           form=form, modo="Editar",
                           accion=url_for("cliente_editar", id=id), registro=cliente)


@app.route("/clientes/eliminar/<int:id>", methods=["POST"])
def cliente_eliminar(id):
    cliente = o_404(datos.obtener_cliente(id))

    # La clave foranea usa ON DELETE RESTRICT: un cliente con facturas
    # no se puede borrar. Se avisa en lenguaje llano en lugar de dejar
    # que salte un error de base de datos. [N9]
    if datos.cliente_tiene_facturas(id):
        flash(f"No se puede eliminar a \"{cliente['nombre']}\": tiene facturas "
              f"emitidas. Elimina primero sus facturas.", "warning")
        return redirect(url_for("clientes"))

    datos.eliminar_cliente(id)
    flash(f"Cliente \"{cliente['nombre']}\" eliminado de la base de datos.", "warning")
    return redirect(url_for("clientes"))


# ============================================================
#  MODULO PROVEEDORES
# ============================================================
@app.route("/proveedores")
def proveedores():
    return render_template("proveedores.html", titulo="Proveedores",
                           proveedores=datos.listar_proveedores())


@app.route("/proveedores/nuevo", methods=["GET", "POST"])
def proveedor_nuevo():
    form = ProveedorForm()

    if form.validate_on_submit():
        datos.crear_proveedor(form.empresa.data.strip(), form.contacto.data.strip(),
                              form.correo.data.strip(), form.telefono.data.strip(),
                              form.ciudad.data.strip(), form.suministra.data.strip())
        flash(f"Proveedor \"{form.empresa.data.strip()}\" agregado a la base de datos.",
              "success")
        return redirect(url_for("proveedores"))

    return render_template("formulario_proveedor.html", titulo="Nuevo proveedor",
                           form=form, modo="Registrar", accion=url_for("proveedor_nuevo"))


@app.route("/proveedores/editar/<int:id>", methods=["GET", "POST"])
def proveedor_editar(id):
    proveedor = o_404(datos.obtener_proveedor(id))
    form = ProveedorForm(data=proveedor)

    if form.validate_on_submit():
        datos.actualizar_proveedor(id, form.empresa.data.strip(), form.contacto.data.strip(),
                                   form.correo.data.strip(), form.telefono.data.strip(),
                                   form.ciudad.data.strip(), form.suministra.data.strip())
        flash(f"Proveedor \"{form.empresa.data.strip()}\" modificado.", "success")
        return redirect(url_for("proveedores"))

    return render_template("formulario_proveedor.html", titulo="Editar proveedor",
                           form=form, modo="Editar",
                           accion=url_for("proveedor_editar", id=id), registro=proveedor)


@app.route("/proveedores/eliminar/<int:id>", methods=["POST"])
def proveedor_eliminar(id):
    proveedor = o_404(datos.obtener_proveedor(id))
    datos.eliminar_proveedor(id)
    flash(f"Proveedor \"{proveedor['empresa']}\" eliminado. Sus productos quedaron "
          f"sin proveedor asignado.", "warning")
    return redirect(url_for("proveedores"))


# ============================================================
#  MODULO FACTURACION
# ============================================================
@app.route("/facturacion")
def facturacion():
    """SELECT con JOIN hacia clientes."""
    return render_template("facturacion.html", titulo="Facturacion",
                           facturas=datos.listar_facturas(),
                           total_facturado=datos.total_facturado())


@app.route("/facturacion/nueva", methods=["GET", "POST"])
def factura_nueva():
    form = FacturaForm()
    cargar_clientes(form)

    if form.validate_on_submit():
        datos.crear_factura(form.numero.data.strip(), form.id_cliente.data,
                            form.fecha.data, float(form.total.data), form.estado.data)
        flash(f"Factura {form.numero.data.strip()} agregada a la base de datos.",
              "success")
        return redirect(url_for("facturacion"))

    return render_template("formulario_facturacion.html", titulo="Nueva factura",
                           form=form, modo="Registrar", accion=url_for("factura_nueva"))


@app.route("/facturacion/editar/<int:id>", methods=["GET", "POST"])
def factura_editar(id):
    factura = o_404(datos.obtener_factura(id))
    form = FacturaForm(data=factura)
    cargar_clientes(form)

    if form.validate_on_submit():
        datos.actualizar_factura(id, form.numero.data.strip(), form.id_cliente.data,
                                 form.fecha.data, float(form.total.data), form.estado.data)
        flash(f"Factura {form.numero.data.strip()} modificada.", "success")
        return redirect(url_for("facturacion"))

    return render_template("formulario_facturacion.html", titulo="Editar factura",
                           form=form, modo="Editar",
                           accion=url_for("factura_editar", id=id), registro=factura)


@app.route("/facturacion/eliminar/<int:id>", methods=["POST"])
def factura_eliminar(id):
    factura = o_404(datos.obtener_factura(id))
    datos.eliminar_factura(id)
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
#  Se ejecuta sql/esquema.sql para asegurar que la base y las
#  tablas existan. Como usa IF NOT EXISTS, no borra nada.
# ============================================================
if __name__ == "__main__":
    with app.app_context():
        datos.inicializar()
    app.run(debug=True)
