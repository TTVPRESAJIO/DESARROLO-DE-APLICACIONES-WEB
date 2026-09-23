# =====================================================================
#  ELECTRIC LIFE · datos.py  (Semana 15)
#  ---------------------------------------------------------------------
#  Capa de acceso a datos sobre PostgreSQL.
#
#  Todas las funciones siguen el mismo patron de las semanas anteriores:
#
#       conn = get_db_connection()          -> conexion centralizada
#       cursor = dict_cursor(conn)          -> filas como diccionario
#       cursor.execute("... %s", (valor,))  -> consulta PARAMETRIZADA
#       conn.commit()                       -> tras INSERT/UPDATE/DELETE
#       cursor.close(); conn.close()        -> cerrar siempre
#
#  Los valores nunca se concatenan dentro del SQL: viajan aparte como
#  parametros, lo que evita la inyeccion de SQL. psycopg2 usa el mismo
#  marcador %s que el conector de MySQL, asi que las consultas de la
#  Semana 13 y 14 se mantienen practicamente iguales.
#
#  QUE CAMBIO AL PASAR DE MySQL A PostgreSQL:
#    · cursor(dictionary=True)  ->  dict_cursor(conn)
#    · cursor.lastrowid         ->  INSERT ... RETURNING id
#    · SHOW TABLES              ->  consulta a information_schema
#
#  Nota sobre los alias: las claves primarias se llaman id_producto,
#  id_cliente, etc. En los SELECT se renombran con "AS id" para que las
#  plantillas Jinja2 de las semanas anteriores sigan funcionando igual.
# =====================================================================
import os
import re
from datetime import datetime

from conexion import (get_db_connection, get_server_connection, dict_cursor,
                      usando_url_de_render)

RUTA_ESQUEMA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "sql", "esquema.sql")


# =====================================================================
#  INICIALIZACION
# =====================================================================
def inicializar():
    """Crea la base y las tablas si aun no existen, ejecutando esquema.sql.

    Como el archivo usa CREATE TABLE IF NOT EXISTS, volver a ejecutarlo
    no borra nada de lo que ya estuviera guardado.

    Funciona igual en local y en Render. La unica diferencia es que en
    local puede hacer falta crear antes la base de datos entera, cosa
    que en Render ya hizo el servicio de PostgreSQL.
    """
    _crear_base_si_falta()

    with open(RUTA_ESQUEMA, "r", encoding="utf-8") as archivo:
        script = archivo.read()

    # Los INSERT de ejemplo solo deben correr la primera vez.
    if _base_con_datos():
        script = script.split("--  DATOS DE EJEMPLO")[0]

    conn = get_db_connection()
    cursor = conn.cursor()
    # psycopg2 acepta varias instrucciones separadas por ";" en una sola
    # llamada, asi que el script se envia completo.
    cursor.execute(script)
    conn.commit()
    cursor.close()
    conn.close()


def _crear_base_si_falta():
    """Crea la base de datos en local si todavia no existe.

    PostgreSQL no admite CREATE DATABASE IF NOT EXISTS, por eso primero
    se consulta el catalogo pg_database y solo despues se crea.

    En Render no se ejecuta: alli la base viene creada y el usuario del
    servicio no tiene permiso para crear otras.
    """
    if usando_url_de_render():
        return

    from conexion.conexion import CONFIG_POR_DEFECTO
    nombre = os.environ.get("PGDATABASE", CONFIG_POR_DEFECTO["PGDATABASE"])

    # El nombre sale de la configuracion, no de un formulario, pero se
    # valida igual porque CREATE DATABASE no admite parametros y hay que
    # escribirlo dentro de la instruccion.
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", nombre):
        raise ValueError(f"Nombre de base de datos no valido: {nombre}")

    conn = get_server_connection()
    conn.autocommit = True          # CREATE DATABASE no admite transaccion
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (nombre,))
    if cursor.fetchone() is None:
        cursor.execute(f'CREATE DATABASE "{nombre}"')
    cursor.close()
    conn.close()


def _base_con_datos():
    """Comprueba si la tabla productos ya tiene registros."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM productos")
        total = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return total > 0
    except Exception:
        return False          # La base o la tabla todavia no existen


def probar_conexion():
    """Devuelve la lista de tablas. Sirve para comprobar la conexion.

    En MySQL esto era SHOW TABLES. PostgreSQL no tiene esa instruccion:
    se consulta el catalogo information_schema, que es estandar SQL.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    tablas = [fila[0] for fila in cursor.fetchall()]
    cursor.close()
    conn.close()
    return tablas


def contar(tabla):
    """Cuenta los registros de una tabla (validada contra lista blanca)."""
    permitidas = {"productos", "clientes", "proveedores", "facturas",
                  "solicitudes", "mensajes"}
    if tabla not in permitidas:
        raise ValueError(f"Tabla no permitida: {tabla}")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total


# =====================================================================
#  MODULO PRODUCTOS  ·  SELECT / INSERT / UPDATE / DELETE completos
# =====================================================================
def listar_productos():
    """LEER · SELECT con JOIN: cada producto junto al nombre de su proveedor.

    Es la consulta relacionada entre dos tablas que exige la actividad:
    productos.id_proveedor -> proveedores.id_proveedor

    Se usa LEFT JOIN y no INNER JOIN para que tambien salgan los
    productos que se quedaron sin proveedor asignado.
    """
    conn = get_db_connection()
    cursor = dict_cursor(conn)
    cursor.execute("""
        SELECT  p.id_producto AS id,
                p.nombre,
                p.categoria,
                p.precio,
                p.stock,
                p.icono,
                p.id_proveedor,
                pr.empresa AS proveedor
        FROM productos p
        LEFT JOIN proveedores pr ON pr.id_proveedor = p.id_proveedor
        ORDER BY p.id_producto
    """)
    productos = cursor.fetchall()
    cursor.close()
    conn.close()
    return productos


def productos_por_proveedor(id_proveedor):
    """Ejemplo de consulta con WHERE sobre la clave foranea."""
    conn = get_db_connection()
    cursor = dict_cursor(conn)
    cursor.execute(
        "SELECT id_producto AS id, nombre, precio FROM productos "
        "WHERE id_proveedor = %s ORDER BY nombre",
        (id_proveedor,))
    productos = cursor.fetchall()
    cursor.close()
    conn.close()
    return productos


def obtener_producto(id_producto):
    """LEER · SELECT ... WHERE: recupera un solo registro por su id."""
    conn = get_db_connection()
    cursor = dict_cursor(conn)
    cursor.execute(
        "SELECT id_producto AS id, nombre, categoria, precio, stock, icono, "
        "       id_proveedor "
        "FROM productos WHERE id_producto = %s",
        (id_producto,))
    producto = cursor.fetchone()
    cursor.close()
    conn.close()
    return producto


def crear_producto(nombre, categoria, precio, stock, icono, id_proveedor):
    """CREAR · INSERT INTO: agrega un producto validado por Flask-WTF.

    psycopg2 no tiene cursor.lastrowid. Para conocer el identificador
    recien generado se usa RETURNING, que es la forma de PostgreSQL.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO productos (nombre, categoria, precio, stock, icono, id_proveedor) "
        "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_producto",
        (nombre, categoria, precio, stock, icono, id_proveedor))
    nuevo_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return nuevo_id


def actualizar_producto(id_producto, nombre, categoria, precio, stock, icono, id_proveedor):
    """ACTUALIZAR · UPDATE ... SET ... WHERE: modifica SOLO ese registro."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE productos SET nombre = %s, categoria = %s, precio = %s, "
        "       stock = %s, icono = %s, id_proveedor = %s "
        "WHERE id_producto = %s",
        (nombre, categoria, precio, stock, icono, id_proveedor, id_producto))
    conn.commit()
    cursor.close()
    conn.close()


def eliminar_producto(id_producto):
    """ELIMINAR · DELETE FROM ... WHERE: borra unicamente ese registro."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
    conn.commit()
    cursor.close()
    conn.close()


def opciones_proveedores():
    """Lista (id, empresa) para el desplegable del formulario."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_proveedor, empresa FROM proveedores ORDER BY empresa")
    opciones = cursor.fetchall()
    cursor.close()
    conn.close()
    return opciones


# =====================================================================
#  MODULO CLIENTES
# =====================================================================
def listar_clientes():
    conn = get_db_connection()
    cursor = dict_cursor(conn)
    cursor.execute(
        "SELECT id_cliente AS id, nombre, cedula, correo, telefono, ciudad, estado "
        "FROM clientes ORDER BY id_cliente")
    clientes = cursor.fetchall()
    cursor.close()
    conn.close()
    return clientes


def contar_clientes_activos():
    """Consulta con WHERE sobre el estado del cliente."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM clientes WHERE estado = %s", ("Activo",))
    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total


def obtener_cliente(id_cliente):
    conn = get_db_connection()
    cursor = dict_cursor(conn)
    cursor.execute(
        "SELECT id_cliente AS id, nombre, cedula, correo, telefono, ciudad, estado "
        "FROM clientes WHERE id_cliente = %s", (id_cliente,))
    cliente = cursor.fetchone()
    cursor.close()
    conn.close()
    return cliente


def crear_cliente(nombre, cedula, correo, telefono, ciudad, estado):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO clientes (nombre, cedula, correo, telefono, ciudad, estado) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (nombre, cedula, correo, telefono, ciudad, estado))
    conn.commit()
    cursor.close()
    conn.close()


def actualizar_cliente(id_cliente, nombre, cedula, correo, telefono, ciudad, estado):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE clientes SET nombre = %s, cedula = %s, correo = %s, "
        "       telefono = %s, ciudad = %s, estado = %s "
        "WHERE id_cliente = %s",
        (nombre, cedula, correo, telefono, ciudad, estado, id_cliente))
    conn.commit()
    cursor.close()
    conn.close()


def eliminar_cliente(id_cliente):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id_cliente = %s", (id_cliente,))
    conn.commit()
    cursor.close()
    conn.close()


def cliente_tiene_facturas(id_cliente):
    """Comprueba la relacion antes de borrar (la FK usa ON DELETE RESTRICT)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM facturas WHERE id_cliente = %s", (id_cliente,))
    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total > 0


def opciones_clientes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_cliente, nombre FROM clientes ORDER BY nombre")
    opciones = cursor.fetchall()
    cursor.close()
    conn.close()
    return opciones


# =====================================================================
#  MODULO PROVEEDORES
# =====================================================================
def listar_proveedores():
    conn = get_db_connection()
    cursor = dict_cursor(conn)
    cursor.execute(
        "SELECT id_proveedor AS id, empresa, contacto, correo, telefono, "
        "       ciudad, suministra "
        "FROM proveedores ORDER BY id_proveedor")
    proveedores = cursor.fetchall()
    cursor.close()
    conn.close()
    return proveedores


def obtener_proveedor(id_proveedor):
    conn = get_db_connection()
    cursor = dict_cursor(conn)
    cursor.execute(
        "SELECT id_proveedor AS id, empresa, contacto, correo, telefono, "
        "       ciudad, suministra "
        "FROM proveedores WHERE id_proveedor = %s", (id_proveedor,))
    proveedor = cursor.fetchone()
    cursor.close()
    conn.close()
    return proveedor


def crear_proveedor(empresa, contacto, correo, telefono, ciudad, suministra):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO proveedores (empresa, contacto, correo, telefono, ciudad, suministra) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (empresa, contacto, correo, telefono, ciudad, suministra))
    conn.commit()
    cursor.close()
    conn.close()


def actualizar_proveedor(id_proveedor, empresa, contacto, correo, telefono, ciudad, suministra):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE proveedores SET empresa = %s, contacto = %s, correo = %s, "
        "       telefono = %s, ciudad = %s, suministra = %s "
        "WHERE id_proveedor = %s",
        (empresa, contacto, correo, telefono, ciudad, suministra, id_proveedor))
    conn.commit()
    cursor.close()
    conn.close()


def eliminar_proveedor(id_proveedor):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM proveedores WHERE id_proveedor = %s", (id_proveedor,))
    conn.commit()
    cursor.close()
    conn.close()


# =====================================================================
#  MODULO FACTURACION
# =====================================================================
def listar_facturas():
    """LEER · SELECT con JOIN: cada factura junto al nombre de su cliente.

    Segunda consulta relacionada del proyecto:
    facturas.id_cliente -> clientes.id_cliente
    """
    conn = get_db_connection()
    cursor = dict_cursor(conn)
    cursor.execute("""
        SELECT  f.id_factura AS id,
                f.numero,
                f.fecha,
                f.total,
                f.estado,
                f.id_cliente,
                c.nombre AS cliente
        FROM facturas f
        INNER JOIN clientes c ON c.id_cliente = f.id_cliente
        ORDER BY f.id_factura
    """)
    facturas = cursor.fetchall()
    cursor.close()
    conn.close()
    return facturas


def total_facturado():
    """Suma en SQL, excluyendo las facturas anuladas (WHERE)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(SUM(total), 0) FROM facturas WHERE estado <> %s",
                   ("Anulada",))
    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return float(total)


def obtener_factura(id_factura):
    conn = get_db_connection()
    cursor = dict_cursor(conn)
    cursor.execute(
        "SELECT id_factura AS id, numero, id_cliente, fecha, total, estado "
        "FROM facturas WHERE id_factura = %s", (id_factura,))
    factura = cursor.fetchone()
    cursor.close()
    conn.close()
    return factura


def crear_factura(numero, id_cliente, fecha, total, estado):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO facturas (numero, id_cliente, fecha, total, estado) "
        "VALUES (%s, %s, %s, %s, %s)",
        (numero, id_cliente, fecha, total, estado))
    conn.commit()
    cursor.close()
    conn.close()


def actualizar_factura(id_factura, numero, id_cliente, fecha, total, estado):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE facturas SET numero = %s, id_cliente = %s, fecha = %s, "
        "       total = %s, estado = %s "
        "WHERE id_factura = %s",
        (numero, id_cliente, fecha, total, estado, id_factura))
    conn.commit()
    cursor.close()
    conn.close()


def eliminar_factura(id_factura):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM facturas WHERE id_factura = %s", (id_factura,))
    conn.commit()
    cursor.close()
    conn.close()


# =====================================================================
#  FORMULARIOS PUBLICOS DE LA PORTADA
# =====================================================================
def crear_solicitud(nombre, categoria, descripcion):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO solicitudes (nombre, categoria, descripcion, fecha) "
        "VALUES (%s, %s, %s, %s) RETURNING id_solicitud",
        (nombre, categoria, descripcion, datetime.now()))
    nuevo_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return nuevo_id


def ultimas_solicitudes(limite=6):
    conn = get_db_connection()
    cursor = dict_cursor(conn)
    cursor.execute(
        "SELECT id_solicitud AS id, nombre, categoria, descripcion, fecha "
        "FROM solicitudes ORDER BY id_solicitud DESC LIMIT %s", (limite,))
    solicitudes = cursor.fetchall()
    cursor.close()
    conn.close()
    return solicitudes


def contar_solicitudes():
    return contar("solicitudes")


def crear_mensaje(nombre, correo, asunto, mensaje):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO mensajes (nombre, correo, asunto, mensaje, fecha) "
        "VALUES (%s, %s, %s, %s, %s)",
        (nombre, correo, asunto, mensaje, datetime.now()))
    conn.commit()
    cursor.close()
    conn.close()
