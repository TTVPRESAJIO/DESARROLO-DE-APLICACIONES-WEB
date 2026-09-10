# =====================================================================
#  ELECTRIC LIFE · conexion/conexion.py  (Semana 13)
#  ---------------------------------------------------------------------
#  Punto UNICO de conexion con la base de datos relacional MySQL.
#  Centralizar la conexion aqui evita repetir los datos de acceso en
#  cada ruta: si manana cambia el servidor, solo se toca este archivo.
#
#  Conector: mysql-connector-python  (pip install mysql-connector-python)
# =====================================================================
import os

import mysql.connector
from flask import current_app


# ---------------------------------------------------------------------
#  Datos de acceso.
#  Se leen de variables de entorno para NO dejar contrasenas reales
#  escritas en el repositorio. Los valores por defecto corresponden a
#  una instalacion de XAMPP recien instalada (root sin contrasena).
# ---------------------------------------------------------------------
CONFIG_POR_DEFECTO = {
    "MYSQL_HOST":     os.environ.get("MYSQL_HOST", "localhost"),
    "MYSQL_USER":     os.environ.get("MYSQL_USER", "root"),
    "MYSQL_PASSWORD": os.environ.get("MYSQL_PASSWORD", ""),
    "MYSQL_DATABASE": os.environ.get("MYSQL_DATABASE", "electric_life_web"),
    "MYSQL_PORT":     int(os.environ.get("MYSQL_PORT", 3306)),
}


def _config(clave):
    """Toma el valor de la configuracion de Flask si hay aplicacion activa.

    Asi la conexion funciona tanto dentro de una ruta (donde existe
    current_app) como en los scripts de inicializacion que se ejecutan
    antes de levantar el servidor.
    """
    try:
        if current_app:
            return current_app.config.get(clave, CONFIG_POR_DEFECTO[clave])
    except RuntimeError:
        pass                      # No hay contexto de aplicacion todavia
    return CONFIG_POR_DEFECTO[clave]


def get_db_connection():
    """Crea y retorna una conexion a la base de datos MySQL."""
    return mysql.connector.connect(
        host=_config("MYSQL_HOST"),
        user=_config("MYSQL_USER"),
        password=_config("MYSQL_PASSWORD"),
        database=_config("MYSQL_DATABASE"),
        port=_config("MYSQL_PORT"),
    )


def get_server_connection():
    """Conexion al servidor SIN elegir base de datos.

    Se usa solo para poder ejecutar CREATE DATABASE la primera vez.
    """
    return mysql.connector.connect(
        host=_config("MYSQL_HOST"),
        user=_config("MYSQL_USER"),
        password=_config("MYSQL_PASSWORD"),
        port=_config("MYSQL_PORT"),
    )
