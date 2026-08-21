# ============================================================
#  ELECTRIC LIFE - Proyecto Integrador (Desarrollo de Aplicaciones Web)
#  Semana 10 - PRUEBA CON BASE DE DATOS
#  Misma aplicacion Flask + Jinja2, pero los datos ahora se leen
#  desde la base de datos relacional "electric_life" (MariaDB / XAMPP),
#  la misma disenada en la asignatura de Bases de Datos.
#  Conector: Flask-SQLAlchemy + PyMySQL.
# ============================================================
import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)

# --- Conexion a MariaDB (XAMPP). Ajusta si tu usuario/clave cambian. ---
DB_USER = os.environ.get("DB_USER", "root")
DB_PASS = os.environ.get("DB_PASS", "")          # XAMPP: root sin contrasena
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "3306")      # XAMPP usa 3306
DB_NAME = os.environ.get("DB_NAME", "electric_life")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

empresa = "Electric Life"

# ======================================================
#  MODELOS: cada clase refleja una tabla de electric_life
# ======================================================
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


@app.route("/")
def index():
    return render_template("index.html", titulo="Inicio", empresa=empresa,
                           total_productos=Producto.query.count(),
                           total_clientes=Cliente.query.count(),
                           total_proveedores=Proveedor.query.count())


@app.route("/productos")
def productos():
    # El stock se obtiene de la VISTA vista_stock_producto (Kardex)
    filas = db.session.execute(text(
        "SELECT p.id_producto, p.nombre_modelo, c.nombre_categoria AS categoria, "
        "       p.precio_venta, COALESCE(v.stock_actual, 0) AS stock "
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
    return render_template("proveedores.html", titulo="Proveedores",
                           proveedores=Proveedor.query.all())


@app.route("/facturacion")
def facturacion():
    ventas = Venta.query.all()
    total_facturado = sum(float(v.total) for v in ventas)
    return render_template("facturacion.html", titulo="Facturacion",
                           ventas=ventas, total_facturado=total_facturado)


if __name__ == "__main__":
    app.run(debug=True)
