# =====================================================================
#  ELECTRIC LIFE · models.py  (Semana 14)
#  ---------------------------------------------------------------------
#  Modelo de usuario del sistema de autenticacion.
#
#  La clase Usuario hereda de UserMixin, que es lo que Flask-Login
#  necesita para manejar la sesion. UserMixin aporta gratis:
#       is_authenticated, is_active, is_anonymous y get_id()
#
#  Las contrasenas NUNCA se guardan en texto plano: se almacena el hash
#  que produce generate_password_hash() y se comprueba con
#  check_password_hash(). El hash es de un solo sentido, asi que ni
#  siquiera quien tenga acceso a la base puede leer la contrasena.
# =====================================================================
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from conexion import get_db_connection


class Usuario(UserMixin):
    """Usuario autorizado para entrar al sistema."""

    def __init__(self, id, usuario, nombre_completo, password_hash=None):
        self.id = id
        self.usuario = usuario
        self.nombre_completo = nombre_completo
        self.password_hash = password_hash

    # -----------------------------------------------------------------
    #  Flask-Login guarda en la sesion el valor que devuelve get_id().
    #  Debe ser texto.
    # -----------------------------------------------------------------
    def get_id(self):
        return str(self.id)

    def verificar_password(self, password):
        """Compara la contrasena escrita con el hash guardado.

        Nunca se comparan las cadenas directamente: check_password_hash
        vuelve a aplicar el mismo algoritmo y compara los resultados.
        """
        return check_password_hash(self.password_hash, password)


# =====================================================================
#  CONSULTAS SOBRE LA TABLA usuarios
#  Todas parametrizadas con %s, igual que el resto del proyecto.
# =====================================================================
def _desde_fila(fila):
    """Convierte una fila de la base en un objeto Usuario."""
    if fila is None:
        return None
    return Usuario(
        id=fila["id"],
        usuario=fila["usuario"],
        nombre_completo=fila["nombre_completo"],
        password_hash=fila["password"],
    )


def obtener_por_id(id_usuario):
    """Recupera un usuario por su identificador. La usa load_user()."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, usuario, nombre_completo, password FROM usuarios WHERE id = %s",
        (id_usuario,))
    fila = cursor.fetchone()
    cursor.close()
    conn.close()
    return _desde_fila(fila)


def obtener_por_usuario(nombre_usuario):
    """Recupera un usuario por su nombre. La usa el login."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, usuario, nombre_completo, password FROM usuarios WHERE usuario = %s",
        (nombre_usuario,))
    fila = cursor.fetchone()
    cursor.close()
    conn.close()
    return _desde_fila(fila)


def existe_usuario(nombre_usuario):
    """Comprueba si el nombre ya esta ocupado (la columna es UNIQUE)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = %s", (nombre_usuario,))
    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total > 0


def crear_usuario(nombre_usuario, nombre_completo, password):
    """Registra un usuario guardando SOLO el hash de la contrasena."""
    hash_password = generate_password_hash(password)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (usuario, nombre_completo, password, fecha_registro) "
        "VALUES (%s, %s, %s, %s)",
        (nombre_usuario, nombre_completo, hash_password, datetime.now()))
    conn.commit()
    nuevo_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return nuevo_id


def contar_usuarios():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total


def listar_usuarios():
    """Listado para el panel. NUNCA devuelve la columna password."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, usuario, nombre_completo, fecha_registro "
        "FROM usuarios ORDER BY id")
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()
    return usuarios
