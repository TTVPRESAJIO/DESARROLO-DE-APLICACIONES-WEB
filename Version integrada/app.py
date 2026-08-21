# =====================================================================
#  ELECTRIC LIFE  ·  Version integrada
#  ---------------------------------------------------------------------
#  Reune el trabajo de las tres asignaturas:
#
#   · Desarrollo de Aplicaciones Web : Flask + Jinja2, plantillas
#     heredadas, componentes reutilizables y contenido dinamico.
#   · Bases de Datos                 : la informacion se lee de la base
#     relacional "electric_life" (MariaDB), incluida la vista del Kardex.
#   · Interaccion Humano-Computador  : capa de usabilidad y accesibilidad
#     (heuristicas de Nielsen + WCAG 2.1 nivel AA).
#
#  Novedad respecto a las versiones anteriores: los formularios ya no
#  solo se validan en el navegador, tambien se validan en el servidor y
#  se GUARDAN en la base de datos.
#
#  Ejecucion local:
#      python app.py      ->      http://127.0.0.1:5000
# =====================================================================
import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)

# Necesario para los mensajes flash (avisos de confirmacion).
app.secret_key = os.environ.get("SECRET_KEY", "electric-life-clave-de-desarrollo")

# --- Conexion a MariaDB (XAMPP). Ajusta si tu usuario/clave cambian. ---
DB_USER = os.environ.get("DB_USER", "root")
DB_PASS = os.environ.get("DB_PASS", "")          # XAMPP: root sin contrasena
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "3306")
DB_NAME = os.environ.get("DB_NAME", "electric_life")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

empresa = "Electric Life"


# =====================================================================
#  MODELOS: cada clase refleja una tabla de electric_life
# =====================================================================
class CategoriaProducto(db.Model):
    __tablename__ = "categoria_producto"
    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre_categoria = db.Column(db.String(60))
    clasificacion_abc = db.Column(db.String(1))


class Producto(db.Model):
    __tablename__ = "producto"
    id_producto = db.Column(db.Integer, primary_key=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey("categoria_producto.id_categoria"))
    nombre_modelo = db.Column(db.String(120))
    marca = db.Column(db.String(60))
    precio_venta = db.Column(db.Numeric(10, 2))
    garantia_meses = db.Column(db.Integer)
    categoria = db.relationship("CategoriaProducto")


class Cliente(db.Model):
    __tablename__ = "cliente"
    id_cliente = db.Column(db.Integer, primary_key=True)
    tipo_cliente = db.Column(db.String(20))
    nombre_razon_social = db.Column(db.String(120))
    ruc_cedula = db.Column(db.String(13))
    telefono = db.Column(db.String(15))
    correo = db.Column(db.String(100))
    ciudad = db.Column(db.String(60))


class Proveedor(db.Model):
    __tablename__ = "proveedor"
    id_proveedor = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    ubicacion = db.Column(db.String(100))
    telefono = db.Column(db.String(15))
    correo = db.Column(db.String(100))
    suministro_principal = db.Column(db.String(200))


class Cotizacion(db.Model):
    __tablename__ = "cotizacion"
    id_cotizacion = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey("cliente.id_cliente"))
    estado = db.Column(db.String(20))
    cliente = db.relationship("Cliente")


class Venta(db.Model):
    __tablename__ = "venta"
    id_venta = db.Column(db.Integer, primary_key=True)
    id_cotizacion = db.Column(db.Integer, db.ForeignKey("cotizacion.id_cotizacion"))
    fecha_venta = db.Column(db.Date)
    forma_pago = db.Column(db.String(20))
    total = db.Column(db.Numeric(10, 2))
    cotizacion = db.relationship("Cotizacion")


# ---------------------------------------------------------------------
#  Tablas propias del sitio web (se crean solas si no existen).
#  No modifican las 16 tablas del diseno original de Bases de Datos.
# ---------------------------------------------------------------------
class SolicitudWeb(db.Model):
    __tablename__ = "solicitud_web"
    id_solicitud = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    categoria = db.Column(db.String(40), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.now)


class MensajeWeb(db.Model):
    __tablename__ = "mensaje_web"
    id_mensaje = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    correo = db.Column(db.String(100), nullable=False)
    asunto = db.Column(db.String(60), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.now)


# =====================================================================
#  CATALOGO UNICO DE SERVICIOS
#  [N4] Consistencia: las tarjetas, la tabla comparativa y el desplegable
#  del formulario se alimentan de esta misma lista, de modo que es
#  imposible que se desincronicen.
# =====================================================================
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

# Opciones de los desplegables (clave guardada -> texto que ve la persona)
CATEGORIAS_SOLICITUD = {
    "instalacion":   "Instalacion de sistema solar",
    "internet":      "Internet sin apagones",
    "mantenimiento": "Mantenimiento de un sistema existente",
    "asesoria":      "Asesoria y cotizacion",
}

ASUNTOS_CONTACTO = {
    "consulta":    "Consulta sobre sistemas solares",
    "cotizacion":  "Solicitud de cotizacion",
    "soporte":     "Soporte tecnico",
    "otro":        "Otro tema",
}


# =====================================================================
#  VALIDACION EN EL SERVIDOR
#  [N5] Prevencion de errores y [N9] recuperacion.
#  La validacion del navegador es una comodidad; esta es la que de
#  verdad protege los datos (funciona aunque se desactive JavaScript).
# =====================================================================
def validar_solicitud(datos):
    errores = {}

    nombre = datos.get("sol_nombre", "").strip()
    if not nombre:
        errores["nombre"] = "Escribe tu nombre para poder contactarte."
    elif len(nombre) < 3:
        errores["nombre"] = "El nombre debe tener al menos 3 caracteres."
    elif len(nombre) > 80:
        errores["nombre"] = "El nombre no puede superar los 80 caracteres."

    categoria = datos.get("sol_categoria", "").strip()
    if not categoria:
        errores["categoria"] = "Elige el tipo de servicio que necesitas."
    elif categoria not in CATEGORIAS_SOLICITUD:
        errores["categoria"] = "Esa opcion no esta disponible."

    descripcion = datos.get("sol_descripcion", "").strip()
    if not descripcion:
        errores["descripcion"] = "Cuentanos brevemente que necesitas."
    elif len(descripcion) < 10:
        errores["descripcion"] = "Describe tu necesidad con al menos 10 caracteres."
    elif len(descripcion) > 500:
        errores["descripcion"] = "La descripcion no puede superar los 500 caracteres."

    return errores


def validar_contacto(datos):
    errores = {}

    nombre = datos.get("con_nombre", "").strip()
    if not nombre:
        errores["nombre"] = "Escribe tu nombre."
    elif len(nombre) < 3:
        errores["nombre"] = "El nombre debe tener al menos 3 caracteres."

    correo = datos.get("con_correo", "").strip()
    if not correo:
        errores["correo"] = "Necesitamos tu correo para responderte."
    elif "@" not in correo or "." not in correo.split("@")[-1]:
        errores["correo"] = "Revisa el formato del correo (ejemplo: nombre@correo.com)."

    asunto = datos.get("con_asunto", "").strip()
    if not asunto:
        errores["asunto"] = "Elige el motivo de tu mensaje."
    elif asunto not in ASUNTOS_CONTACTO:
        errores["asunto"] = "Ese motivo no esta disponible."

    mensaje = datos.get("con_mensaje", "").strip()
    if not mensaje:
        errores["mensaje"] = "Escribe tu mensaje."
    elif len(mensaje) < 15:
        errores["mensaje"] = "El mensaje debe tener al menos 15 caracteres."
    elif len(mensaje) > 1000:
        errores["mensaje"] = "El mensaje no puede superar los 1000 caracteres."

    return errores


def datos_portada(**extra):
    """Informacion comun que necesita la portada."""
    contexto = {
        "titulo": "Inicio",
        "empresa": empresa,
        "servicios": SERVICIOS,
        "categorias": CATEGORIAS_SOLICITUD,
        "asuntos": ASUNTOS_CONTACTO,
        "solicitudes": SolicitudWeb.query.order_by(SolicitudWeb.id_solicitud.desc()).limit(6).all(),
        "total_solicitudes": SolicitudWeb.query.count(),
        "total_productos": Producto.query.count(),
        "total_clientes": Cliente.query.count(),
        "total_proveedores": Proveedor.query.count(),
        "errores": {},
        "previos": {},
    }
    contexto.update(extra)
    return contexto


# =====================================================================
#  RUTAS
# =====================================================================
@app.route("/", methods=["GET", "POST"])
def index():
    """Portada informativa. Tambien recibe los dos formularios."""
    if request.method == "POST":
        formulario = request.form.get("formulario", "")

        # Campo trampa: invisible para las personas, atractivo para los
        # robots. Sustituye al captcha, que es una barrera de accesibilidad.
        if request.form.get("web_url", "").strip():
            return redirect(url_for("index") + "#solicitudes")

        if formulario == "solicitud":
            errores = validar_solicitud(request.form)
            if errores:
                return render_template("index.html", **datos_portada(
                    errores={"solicitud": errores},
                    previos={"solicitud": request.form},
                    aviso=("error", "solicitud",
                           "Revisa los campos marcados: faltan datos por corregir."),
                ))

            registro = SolicitudWeb(
                nombre=request.form["sol_nombre"].strip(),
                categoria=request.form["sol_categoria"].strip(),
                descripcion=request.form["sol_descripcion"].strip(),
            )
            db.session.add(registro)
            db.session.commit()
            flash(f"Solicitud registrada correctamente. "
                  f"Tu numero de caso es el #{registro.id_solicitud}. "
                  f"Te contactaremos en un plazo de 24 a 48 horas.", "solicitud")
            return redirect(url_for("index") + "#solicitudes")

        if formulario == "contacto":
            errores = validar_contacto(request.form)
            if errores:
                return render_template("index.html", **datos_portada(
                    errores={"contacto": errores},
                    previos={"contacto": request.form},
                    aviso=("error", "contacto",
                           "Revisa los campos marcados: faltan datos por corregir."),
                ))

            mensaje = MensajeWeb(
                nombre=request.form["con_nombre"].strip(),
                correo=request.form["con_correo"].strip(),
                asunto=request.form["con_asunto"].strip(),
                mensaje=request.form["con_mensaje"].strip(),
            )
            db.session.add(mensaje)
            db.session.commit()
            flash("Mensaje enviado. Respondemos en un plazo de 24 a 48 horas laborables.", "contacto")
            return redirect(url_for("index") + "#contacto")

    return render_template("index.html", **datos_portada())


@app.route("/productos")
def productos():
    """Catalogo leido de la base: el stock sale de la vista del Kardex."""
    filas = db.session.execute(text(
        "SELECT p.id_producto, p.nombre_modelo, p.marca, "
        "       c.nombre_categoria AS categoria, p.precio_venta, "
        "       COALESCE(v.stock_actual, 0) AS stock "
        "FROM producto p "
        "JOIN categoria_producto c ON c.id_categoria = p.id_categoria "
        "LEFT JOIN vista_stock_producto v ON v.id_producto = p.id_producto "
        "ORDER BY p.id_producto")).mappings().all()
    return render_template("productos.html", titulo="Productos",
                           productos=filas, total=len(filas))


@app.route("/clientes")
def clientes():
    lista = Cliente.query.all()
    return render_template("clientes.html", titulo="Clientes",
                           clientes=lista, total=len(lista))


@app.route("/proveedores")
def proveedores():
    lista = Proveedor.query.all()
    return render_template("proveedores.html", titulo="Proveedores",
                           proveedores=lista, total=len(lista))


@app.route("/facturacion")
def facturacion():
    ventas = Venta.query.all()
    total_facturado = sum(float(v.total) for v in ventas)
    return render_template("facturacion.html", titulo="Facturacion",
                           ventas=ventas, total_facturado=total_facturado)


# ---------------------------------------------------------------------
#  Pagina de error amable.
#  [N9] El mensaje se expresa en lenguaje llano, explica el problema y
#  ofrece una salida en lugar de dejar al usuario sin rumbo.
# ---------------------------------------------------------------------
@app.errorhandler(404)
def no_encontrado(e):
    return render_template("404.html", titulo="Pagina no encontrada"), 404


# =====================================================================
#  ARRANQUE
# =====================================================================
if __name__ == "__main__":
    with app.app_context():
        # Crea unicamente las tablas del sitio web que aun no existan.
        db.create_all()
    app.run(debug=True)
