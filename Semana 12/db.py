# =====================================================================
#  ELECTRIC LIFE · db.py  (Semana 12)
#  ---------------------------------------------------------------------
#  Persistencia de datos en un entorno local con SQLite.
#
#  Se usa el modulo sqlite3 de la libreria estandar de Python, siguiendo
#  el patron visto en clase:
#
#       conn = sqlite3.connect(...)      -> abrir la conexion
#       cursor = conn.cursor()           -> crear el cursor
#       cursor.execute("... ?", datos)   -> consulta PARAMETRIZADA
#       conn.commit()                    -> confirmar los cambios
#       conn.close()                     -> cerrar la conexion
#
#  Todas las consultas usan marcadores "?" en lugar de concatenar los
#  valores recibidos del formulario. Eso evita la inyeccion de SQL: el
#  valor viaja aparte de la instruccion, asi que nunca puede ser
#  interpretado como codigo.
# =====================================================================
import os
import sqlite3
from datetime import date, datetime

# El archivo de la base vive en data/ferreteria.db, junto al proyecto.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARPETA_DATOS = os.path.join(BASE_DIR, "data")
RUTA_BD = os.path.join(CARPETA_DATOS, "ferreteria.db")


# ---------------------------------------------------------------------
#  Conversores de fecha.
#  SQLite guarda texto; estos adaptadores permiten seguir trabajando
#  con objetos date y datetime de Python, como en las semanas anteriores.
# ---------------------------------------------------------------------
sqlite3.register_adapter(date, lambda d: d.isoformat())
sqlite3.register_adapter(datetime, lambda d: d.isoformat(sep=" "))
sqlite3.register_converter("DATE", lambda b: date.fromisoformat(b.decode()))
sqlite3.register_converter("TIMESTAMP", lambda b: datetime.fromisoformat(b.decode()))


def conectar():
    """Abre una conexion con la base de datos local.

    row_factory = sqlite3.Row hace que cada fila se pueda leer por el
    nombre de la columna (fila["nombre"]), de modo que las plantillas
    Jinja2 siguen funcionando igual que cuando los datos eran
    diccionarios de Python.
    """
    os.makedirs(CARPETA_DATOS, exist_ok=True)
    conn = sqlite3.connect(RUTA_BD, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn


# =====================================================================
#  CREACION DE LAS TABLAS
#  CREATE TABLE IF NOT EXISTS evita errores al volver a ejecutar la
#  aplicacion y, sobre todo, NO borra lo que ya estaba guardado.
# =====================================================================
def crear_tablas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre    TEXT    NOT NULL,
            categoria TEXT    NOT NULL,
            precio    REAL    NOT NULL,
            stock     INTEGER NOT NULL,
            icono     TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre   TEXT NOT NULL,
            cedula   TEXT NOT NULL,
            correo   TEXT NOT NULL,
            telefono TEXT NOT NULL,
            ciudad   TEXT NOT NULL,
            estado   TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proveedores (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa    TEXT NOT NULL,
            contacto   TEXT NOT NULL,
            correo     TEXT NOT NULL,
            telefono   TEXT NOT NULL,
            ciudad     TEXT NOT NULL,
            suministra TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS facturas (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            numero  TEXT NOT NULL,
            cliente TEXT NOT NULL,
            fecha   DATE NOT NULL,
            total   REAL NOT NULL,
            estado  TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS solicitudes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre      TEXT NOT NULL,
            categoria   TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            fecha       TIMESTAMP NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mensajes (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre  TEXT NOT NULL,
            correo  TEXT NOT NULL,
            asunto  TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            fecha   TIMESTAMP NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# =====================================================================
#  DATOS INICIALES
#  Solo se insertan la PRIMERA vez, cuando la tabla esta vacia. Asi la
#  base no se reinicia en cada arranque y lo que registre el usuario se
#  conserva.
# =====================================================================
def sembrar_datos_iniciales():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM productos")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO productos (nombre, categoria, precio, stock, icono) "
            "VALUES (?, ?, ?, ?, ?)",
            [
                ("Panel Solar Monocristalino 450W", "Panel Solar", 180.00, 24, "bi-sun"),
                ("Inversor Hibrido 3kW",            "Inversor",    650.00, 8,  "bi-lightning-charge"),
                ("Bateria de Litio 100Ah",          "Bateria",     520.00, 12, "bi-battery-full"),
                ("Regulador MPPT 60A",              "Regulador",   140.00, 15, "bi-sliders"),
                ("Breaker DC 63A",                  "Proteccion",  25.00,  40, "bi-shield-check"),
                ("Cable Fotovoltaico 6mm (metro)",  "Cableado",    2.50,  300, "bi-plug"),
                ("Estructura de Montaje Aluminio",  "Estructura",  45.00,  0,  "bi-grid-3x3"),
                ("Controlador de Carga PWM 30A",    "Regulador",   60.00,  0,  "bi-sliders"),
            ])

    cursor.execute("SELECT COUNT(*) FROM clientes")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO clientes (nombre, cedula, correo, telefono, ciudad, estado) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            [
                ("Farmacia Su Salud",         "1690012345001", "farmaciasusalud@gmail.com", "032885001", "Puyo", "Activo"),
                ("Ferreteria El Constructor", "1690023456001", "elconstructor@gmail.com",   "032885002", "Puyo", "Activo"),
                ("Restaurante El Jardin",     "1690034567001", "eljardinpuyo@gmail.com",    "032885003", "Puyo", "Inactivo"),
                ("Juan Andres Perez",         "1600456789",    "juanperez@gmail.com",       "0991112233","Puyo", "Activo"),
                ("Cyber Amazonia",            "1690045678001", "cyberamazonia@gmail.com",   "032885004", "Puyo", "Activo"),
            ])

    cursor.execute("SELECT COUNT(*) FROM proveedores")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO proveedores (empresa, contacto, correo, telefono, ciudad, suministra) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            [
                ("Proviento",    "Ventas Proviento", "ventas@proviento.com.ec", "022500000", "Quito",    "Paneles, inversores y baterias"),
                ("Pintulac",     "Atencion Cliente", "info@pintulac.com.ec",    "1800746852","Nacional", "Paneles, inversores y baterias"),
                ("Sunny Future", "Ventas SF",        "info@sunnyfuture.co",     "022600000", "Quito",    "Baterias de litio e inversores"),
                ("Amawtec",      "Distribucion",     "ventas@amawtec.com",      "062600000", "Ibarra",   "Kits fotovoltaicos Growatt"),
            ])

    cursor.execute("SELECT COUNT(*) FROM facturas")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO facturas (numero, cliente, fecha, total, estado) VALUES (?, ?, ?, ?, ?)",
            [
                ("001-001-000001", "Farmacia Su Salud",         date(2026, 7, 12), 2730.00, "Pagada"),
                ("001-001-000002", "Cyber Amazonia",            date(2026, 7, 23), 1530.00, "Pagada"),
                ("001-001-000003", "Ferreteria El Constructor", date(2026, 7, 28), 890.00,  "Pendiente"),
                ("001-001-000004", "Juan Andres Perez",         date(2026, 8, 2),  420.00,  "Pendiente"),
                ("001-001-000005", "Restaurante El Jardin",     date(2026, 8, 5),  310.00,  "Anulada"),
            ])

    conn.commit()
    conn.close()


def iniciar():
    """Prepara la base de datos al arrancar la aplicacion."""
    crear_tablas()
    sembrar_datos_iniciales()


# =====================================================================
#  MODULO PRODUCTOS
# =====================================================================
def listar_productos():
    """SELECT + fetchall(): recupera todos los productos guardados."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos ORDER BY id")
    productos = cursor.fetchall()
    conn.close()
    return productos


def obtener_producto(id_producto):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos WHERE id = ?", (id_producto,))
    producto = cursor.fetchone()
    conn.close()
    return producto


def crear_producto(nombre, categoria, precio, stock, icono):
    """INSERT parametrizado: los valores viajan aparte de la instruccion."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO productos (nombre, categoria, precio, stock, icono) "
        "VALUES (?, ?, ?, ?, ?)",
        (nombre, categoria, precio, stock, icono))
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    return nuevo_id


def actualizar_producto(id_producto, nombre, categoria, precio, stock, icono):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE productos SET nombre = ?, categoria = ?, precio = ?, "
        "stock = ?, icono = ? WHERE id = ?",
        (nombre, categoria, precio, stock, icono, id_producto))
    conn.commit()
    conn.close()


def eliminar_producto(id_producto):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
    conn.commit()
    conn.close()


# =====================================================================
#  MODULO CLIENTES
# =====================================================================
def listar_clientes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes ORDER BY id")
    clientes = cursor.fetchall()
    conn.close()
    return clientes


def contar_clientes_activos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM clientes WHERE estado = ?", ("Activo",))
    total = cursor.fetchone()[0]
    conn.close()
    return total


def obtener_cliente(id_cliente):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE id = ?", (id_cliente,))
    cliente = cursor.fetchone()
    conn.close()
    return cliente


def crear_cliente(nombre, cedula, correo, telefono, ciudad, estado):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO clientes (nombre, cedula, correo, telefono, ciudad, estado) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (nombre, cedula, correo, telefono, ciudad, estado))
    conn.commit()
    conn.close()


def actualizar_cliente(id_cliente, nombre, cedula, correo, telefono, ciudad, estado):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE clientes SET nombre = ?, cedula = ?, correo = ?, telefono = ?, "
        "ciudad = ?, estado = ? WHERE id = ?",
        (nombre, cedula, correo, telefono, ciudad, estado, id_cliente))
    conn.commit()
    conn.close()


def eliminar_cliente(id_cliente):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id = ?", (id_cliente,))
    conn.commit()
    conn.close()


# =====================================================================
#  MODULO PROVEEDORES
# =====================================================================
def listar_proveedores():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM proveedores ORDER BY id")
    proveedores = cursor.fetchall()
    conn.close()
    return proveedores


def obtener_proveedor(id_proveedor):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM proveedores WHERE id = ?", (id_proveedor,))
    proveedor = cursor.fetchone()
    conn.close()
    return proveedor


def crear_proveedor(empresa, contacto, correo, telefono, ciudad, suministra):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO proveedores (empresa, contacto, correo, telefono, ciudad, suministra) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (empresa, contacto, correo, telefono, ciudad, suministra))
    conn.commit()
    conn.close()


def actualizar_proveedor(id_proveedor, empresa, contacto, correo, telefono, ciudad, suministra):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE proveedores SET empresa = ?, contacto = ?, correo = ?, telefono = ?, "
        "ciudad = ?, suministra = ? WHERE id = ?",
        (empresa, contacto, correo, telefono, ciudad, suministra, id_proveedor))
    conn.commit()
    conn.close()


def eliminar_proveedor(id_proveedor):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM proveedores WHERE id = ?", (id_proveedor,))
    conn.commit()
    conn.close()


# =====================================================================
#  MODULO FACTURACION
# =====================================================================
def listar_facturas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM facturas ORDER BY id")
    facturas = cursor.fetchall()
    conn.close()
    return facturas


def total_facturado():
    """Suma solo las facturas que no estan anuladas (calculo en SQL)."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(SUM(total), 0) FROM facturas WHERE estado != ?",
                   ("Anulada",))
    total = cursor.fetchone()[0]
    conn.close()
    return total


def obtener_factura(id_factura):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM facturas WHERE id = ?", (id_factura,))
    factura = cursor.fetchone()
    conn.close()
    return factura


def crear_factura(numero, cliente, fecha, total, estado):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO facturas (numero, cliente, fecha, total, estado) "
        "VALUES (?, ?, ?, ?, ?)",
        (numero, cliente, fecha, total, estado))
    conn.commit()
    conn.close()


def actualizar_factura(id_factura, numero, cliente, fecha, total, estado):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE facturas SET numero = ?, cliente = ?, fecha = ?, total = ?, "
        "estado = ? WHERE id = ?",
        (numero, cliente, fecha, total, estado, id_factura))
    conn.commit()
    conn.close()


def eliminar_factura(id_factura):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM facturas WHERE id = ?", (id_factura,))
    conn.commit()
    conn.close()


# =====================================================================
#  FORMULARIOS PUBLICOS DE LA PORTADA
# =====================================================================
def crear_solicitud(nombre, categoria, descripcion):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO solicitudes (nombre, categoria, descripcion, fecha) "
        "VALUES (?, ?, ?, ?)",
        (nombre, categoria, descripcion, datetime.now()))
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    return nuevo_id


def ultimas_solicitudes(limite=6):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM solicitudes ORDER BY id DESC LIMIT ?", (limite,))
    solicitudes = cursor.fetchall()
    conn.close()
    return solicitudes


def contar_solicitudes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM solicitudes")
    total = cursor.fetchone()[0]
    conn.close()
    return total


def crear_mensaje(nombre, correo, asunto, mensaje):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO mensajes (nombre, correo, asunto, mensaje, fecha) "
        "VALUES (?, ?, ?, ?, ?)",
        (nombre, correo, asunto, mensaje, datetime.now()))
    conn.commit()
    conn.close()


def contar(tabla):
    """Cuenta los registros de una tabla del proyecto.

    El nombre de la tabla NO puede ir como parametro "?" en SQL, por eso
    se valida contra una lista blanca antes de construir la consulta.
    """
    permitidas = {"productos", "clientes", "proveedores", "facturas",
                  "solicitudes", "mensajes"}
    if tabla not in permitidas:
        raise ValueError(f"Tabla no permitida: {tabla}")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
    total = cursor.fetchone()[0]
    conn.close()
    return total
