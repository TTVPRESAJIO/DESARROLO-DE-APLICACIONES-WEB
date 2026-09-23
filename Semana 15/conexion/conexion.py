# =====================================================================
#  ELECTRIC LIFE · conexion/conexion.py  (Semana 15)
#  ---------------------------------------------------------------------
#  Punto UNICO de conexion con la base de datos relacional PostgreSQL.
#
#  Conector: psycopg2  (pip install psycopg2-binary)
#
#  La aplicacion tiene que funcionar en dos sitios distintos:
#
#    1) En el computador local, contra un PostgreSQL instalado aqui.
#       Los datos de acceso se leen de variables de entorno sueltas
#       (PGHOST, PGUSER, PGPASSWORD, PGDATABASE, PGPORT).
#
#    2) En Render, donde el servicio de base de datos entrega una sola
#       variable llamada DATABASE_URL con todo dentro:
#
#           postgresql://usuario:clave@servidor:5432/nombre_base
#
#  Por eso get_db_connection() mira primero DATABASE_URL y, si no
#  existe, arma la conexion con los parametros sueltos. Asi el MISMO
#  codigo corre en local y en produccion sin tocar nada.
#
#  IMPORTANTE: aqui no hay ninguna contrasena real escrita. Todo sale
#  de variables de entorno, que en Render se configuran desde el panel.
# =====================================================================
import os

import psycopg2
import psycopg2.extras
from flask import current_app


# ---------------------------------------------------------------------
#  Valores por defecto para trabajar en local.
#  Corresponden a un PostgreSQL recien instalado (usuario postgres).
# ---------------------------------------------------------------------
CONFIG_POR_DEFECTO = {
    "DATABASE_URL": os.environ.get("DATABASE_URL", ""),
    "PGHOST":       os.environ.get("PGHOST", "localhost"),
    "PGUSER":       os.environ.get("PGUSER", "postgres"),
    "PGPASSWORD":   os.environ.get("PGPASSWORD", "postgres"),
    "PGDATABASE":   os.environ.get("PGDATABASE", "electric_life_web"),
    "PGPORT":       int(os.environ.get("PGPORT", 5432)),
}


def _config(clave):
    """Toma el valor de la configuracion de Flask si hay aplicacion activa.

    Asi la conexion funciona tanto dentro de una ruta (donde existe
    current_app) como en los scripts que se ejecutan antes de levantar
    el servidor.
    """
    try:
        if current_app:
            return current_app.config.get(clave, CONFIG_POR_DEFECTO[clave])
    except RuntimeError:
        pass                      # No hay contexto de aplicacion todavia
    return CONFIG_POR_DEFECTO[clave]


def _normalizar_url(url):
    """Render entrega la URL empezando por postgres://.

    psycopg2 entiende las dos formas, pero se deja en la forma larga
    (postgresql://) porque es la oficial y evita sorpresas.
    """
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def get_db_connection():
    """Crea y retorna una conexion a la base de datos PostgreSQL."""
    url = _config("DATABASE_URL")

    if url:
        # --- Caso Render (produccion) ---------------------------------
        # La URL trae servidor, usuario, clave, puerto y nombre de base.
        #
        # No se fuerza ningun sslmode: psycopg2 usa por defecto "prefer",
        # que intenta cifrar y solo sigue sin cifrado si el servidor no
        # lo admite. Asi sirve igual para la direccion interna de Render
        # y para la externa, que si exige SSL. Si alguna vez hiciera
        # falta obligar, basta con anadir ?sslmode=require a la URL.
        return psycopg2.connect(_normalizar_url(url))

    # --- Caso local -------------------------------------------------
    return psycopg2.connect(
        host=_config("PGHOST"),
        user=_config("PGUSER"),
        password=_config("PGPASSWORD"),
        dbname=_config("PGDATABASE"),
        port=_config("PGPORT"),
    )


def usando_url_de_render():
    """True cuando la conexion se hace por DATABASE_URL (produccion).

    Sirve para saltarse los pasos que solo tienen sentido en local,
    como crear la base de datos la primera vez.
    """
    return bool(_config("DATABASE_URL"))


def get_server_connection():
    """Conexion a la base de mantenimiento 'postgres', SIN elegir base.

    PostgreSQL no admite CREATE DATABASE IF NOT EXISTS, y tampoco deja
    crear una base desde dentro de otra sesion abierta sobre ella. Por
    eso, para crear electric_life_web la primera vez en local, hay que
    entrar por la base de sistema 'postgres'.

    En Render no se usa: alli la base ya viene creada por el servicio.
    """
    return psycopg2.connect(
        host=_config("PGHOST"),
        user=_config("PGUSER"),
        password=_config("PGPASSWORD"),
        dbname="postgres",
        port=_config("PGPORT"),
    )


def dict_cursor(conn):
    """Cursor que devuelve cada fila como un diccionario.

    Es el equivalente en psycopg2 del cursor(dictionary=True) que usaba
    el conector de MySQL en las semanas anteriores. Gracias a esto las
    plantillas Jinja2 siguen escribiendo producto.nombre sin cambios.
    """
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
