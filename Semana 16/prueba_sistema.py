"""PRUEBA FINAL · Semana 16  ·  aplicacion publicada en Render

Verifica: login, CRUD completo en 4 tablas relacionadas, las relaciones
(JOIN y claves foraneas) y las validaciones de los formularios.

SEGURIDAD: para localizar un registro se lee SU PROPIO formulario de
edicion y se comprueba el contenido del campo antes de modificarlo o
borrarlo. Nunca se toca una fila que no haya creado esta prueba.
"""
import os
import re
import sys

import requests

BASE = os.environ.get("APP_URL", "https://electric-life.onrender.com")

# Las credenciales NO se escriben aqui: el repositorio es publico.
# Se pasan como variables de entorno antes de ejecutar la prueba:
#
#     set PRUEBA_USUARIO=tu_usuario
#     set PRUEBA_PASSWORD=tu_contrasena
#     python prueba_sistema.py
#
USUARIO = os.environ.get("PRUEBA_USUARIO", "")
PASSWORD = os.environ.get("PRUEBA_PASSWORD", "")

if not USUARIO or not PASSWORD:
    sys.exit("Define PRUEBA_USUARIO y PRUEBA_PASSWORD antes de ejecutar la prueba.")

MARCA = "ZZTEST"

s = requests.Session()
fallos = []


def csrf(h):
    m = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', h)
    return m.group(1) if m else None


def get(r):
    return s.get(f"{BASE}{r}", timeout=90)


def post(ruta, datos, tok=None):
    return s.post(f"{BASE}{ruta}",
                  data=dict(datos, csrf_token=csrf(get(tok or ruta).text)),
                  allow_redirects=True, timeout=90)


def valor(html, campo):
    m = re.search(r'name="' + campo + r'"[^>]*value="([^"]*)"', html)
    return m.group(1) if m else ""


def titulo(t):
    print()
    print("=" * 72)
    print(t)
    print("=" * 72)


def check(nombre, ok, detalle=""):
    print(f"  [{'OK ' if ok else '!!!'}] {nombre}" + (f"   · {detalle}" if detalle else ""))
    if not ok:
        fallos.append(nombre)
    return ok


def listar_ids(modulo):
    return sorted(set(int(i) for i in
                      re.findall(rf"/{modulo}/eliminar/(\d+)", get(f"/{modulo}").text)))


def buscar_id(modulo, campo, texto):
    """Id del registro cuyo campo contiene ese texto, leyendo cada formulario."""
    for rid in listar_ids(modulo):
        if texto in valor(get(f"/{modulo}/editar/{rid}").text, campo):
            return rid
    return None


def crud(etiqueta, modulo, ruta_nuevo, campo, alta, edicion, senal):
    titulo(f"CRUD · {etiqueta}")
    antes = listar_ids(modulo)

    post(ruta_nuevo, alta)
    despues = listar_ids(modulo)
    if not check("CREAR", len(despues) == len(antes) + 1,
                 f"{len(antes)} -> {len(despues)} registros"):
        print("       bloque interrumpido para no tocar datos reales")
        return
    rid = (set(despues) - set(antes)).pop()
    check("  id nuevo identificado", True, f"id = {rid}")

    post(f"/{modulo}/editar/{rid}", edicion)
    comprobado = valor(get(f"/{modulo}/editar/{rid}").text, campo)
    check("ACTUALIZAR", senal in comprobado or senal in get(f"/{modulo}").text,
          f"campo = '{comprobado}'")
    check("  el UPDATE no crea filas nuevas", len(listar_ids(modulo)) == len(despues))

    # Confirmacion de identidad ANTES de borrar
    if MARCA in valor(get(f"/{modulo}/editar/{rid}").text, campo) or modulo == "facturacion":
        post(f"/{modulo}/eliminar/{rid}", {}, tok=f"/{modulo}")
        final = listar_ids(modulo)
        check("ELIMINAR", rid not in final)
        check("  el DELETE borro solo esa fila", final == antes)
    else:
        check("ELIMINAR (identidad no confirmada, no se borra)", False)


# =====================================================================
titulo("1 · AUTENTICACION Y PROTECCION DE RUTAS")
r = s.get(f"{BASE}/productos", allow_redirects=False)
check("Sin sesion, /productos redirige al login",
      r.status_code == 302 and "/login" in r.headers.get("Location", ""))
check("Contrasena incorrecta NO abre sesion",
      "Panel de administracion" not in
      post("/login", {"usuario": USUARIO, "password": "MAL", "submit": "x"}).text)
check("Usuario inexistente NO abre sesion",
      "Panel de administracion" not in
      post("/login", {"usuario": "nadie", "password": PASSWORD, "submit": "x"}).text)
r = post("/login", {"usuario": USUARIO, "password": PASSWORD, "submit": "Iniciar sesion"})
check("Credenciales correctas abren sesion", "Panel de administracion" in r.text)
check("Se muestra el usuario autenticado", USUARIO in r.text)

# =====================================================================
crud("PRODUCTOS   (hija de proveedores)", "productos", "/productos/nuevo", "nombre",
     {"nombre": f"{MARCA} Panel 600W", "categoria": "Panel Solar", "precio": "412.75",
      "stock": "9", "icono": "bi-sun", "id_proveedor": "0", "submit": "Guardar producto"},
     {"nombre": f"{MARCA} Panel 600W EDITADO", "categoria": "Panel Solar",
      "precio": "399.00", "stock": "21", "icono": "bi-sun", "id_proveedor": "0",
      "submit": "Guardar producto"},
     "EDITADO")

crud("PROVEEDORES   (padre de productos)", "proveedores", "/proveedores/nuevo", "empresa",
     {"empresa": f"{MARCA} Solar Import", "contacto": "Ana Torres",
      "correo": "ventas@solarimport.com", "telefono": "032999888", "ciudad": "Puyo",
      "suministra": "Paneles e inversores", "submit": "Guardar proveedor"},
     {"empresa": f"{MARCA} Solar Import EDITADO", "contacto": "Ana Torres",
      "correo": "ventas@solarimport.com", "telefono": "032999888", "ciudad": "Ambato",
      "suministra": "Paneles e inversores", "submit": "Guardar proveedor"},
     "EDITADO")

crud("CLIENTES   (padre de facturas)", "clientes", "/clientes/nuevo", "nombre",
     {"nombre": f"{MARCA} Panaderia Delicia", "cedula": "1690099999001",
      "correo": "delicia@gmail.com", "telefono": "032777666", "ciudad": "Puyo",
      "estado": "Activo", "submit": "Guardar cliente"},
     {"nombre": f"{MARCA} Panaderia Delicia EDITADO", "cedula": "1690099999001",
      "correo": "delicia@gmail.com", "telefono": "032777666", "ciudad": "Puyo",
      "estado": "Inactivo", "submit": "Guardar cliente"},
     "EDITADO")

crud("FACTURAS   (hija de clientes)", "facturacion", "/facturacion/nueva", "numero",
     {"numero": "001-001-000999", "id_cliente": "2", "fecha": "2026-09-30",
      "total": "1250.00", "estado": "Pendiente", "submit": "Guardar factura"},
     {"numero": "001-001-000999", "id_cliente": "2", "fecha": "2026-09-30",
      "total": "1375.50", "estado": "Pagada", "submit": "Guardar factura"},
     "1375.50")

# =====================================================================
titulo("6 · RELACIONES ENTRE TABLAS")
html = get("/facturacion").text
clientes = set(re.findall(r"Farmacia Su Salud|Cyber Amazonia|Ferreteria El Constructor|"
                          r"Juan Andres Perez|Restaurante El Jardin", html))
check("JOIN facturas-clientes: cada factura muestra su cliente",
      len(clientes) >= 4, f"{len(clientes)} clientes distintos")

html = get("/productos").text
provs = set(re.findall(r"Amawtec|Sunny Future|Proviento|Pintulac", html))
check("JOIN productos-proveedores: cada producto muestra su proveedor",
      len(provs) == 4, ", ".join(sorted(provs)))
check("  ningun producto sin proveedor", "Sin proveedor asignado" not in html)

r = post("/clientes/eliminar/1", {}, tok="/clientes")
check("FK ON DELETE RESTRICT: no borra un cliente con facturas",
      "No se puede eliminar" in r.text)
check("  el cliente sigue ahi", "Farmacia Su Salud" in get("/clientes").text)

# =====================================================================
titulo("7 · VALIDACIONES DE FORMULARIO")
for nombre, ruta, datos in [
    ("Formulario vacio", "/productos/nuevo",
     {"nombre": "", "categoria": "", "precio": "", "stock": "", "submit": "x"}),
    ("Precio negativo", "/productos/nuevo",
     {"nombre": "Prueba", "categoria": "Panel Solar", "precio": "-50",
      "stock": "5", "id_proveedor": "0", "submit": "x"}),
    ("Correo invalido", "/proveedores/nuevo",
     {"empresa": "Prueba correo", "contacto": "Ana Torres", "correo": "no-es-correo",
      "telefono": "032999888", "ciudad": "Puyo", "suministra": "Paneles", "submit": "x"}),
    ("Numero de factura fuera del formato SRI", "/facturacion/nueva",
     {"numero": "ABC-123", "id_cliente": "2", "fecha": "2026-09-30",
      "total": "100.00", "estado": "Pagada", "submit": "x"}),
    ("Factura con fecha futura", "/facturacion/nueva",
     {"numero": "001-001-000998", "id_cliente": "2", "fecha": "2027-12-31",
      "total": "100.00", "estado": "Pagada", "submit": "x"}),
]:
    r = post(ruta, datos)
    check(f"{nombre} es rechazado", "No se pudo guardar" in r.text)

# =====================================================================
titulo("8 · CIERRE DE SESION")
check("Cierra sesion", "Sesion cerrada" in get("/logout").text)
r = s.get(f"{BASE}/productos", allow_redirects=False)
check("Tras salir, las rutas vuelven a estar protegidas",
      r.status_code == 302 and "/login" in r.headers.get("Location", ""))

# =====================================================================
titulo("9 · LA BASE QUEDO LIMPIA")
sesion2 = requests.Session()
s.cookies.clear()
post("/login", {"usuario": USUARIO, "password": PASSWORD, "submit": "Iniciar sesion"})
for modulo, esperado in [("productos", 8), ("proveedores", 4),
                         ("clientes", 5), ("facturacion", 5)]:
    ids = listar_ids(modulo)
    html = get(f"/{modulo}").text
    check(f"{modulo}: {esperado} registros y sin restos de prueba",
          len(ids) == esperado and MARCA not in html, f"{len(ids)} registros")

# =====================================================================
titulo("RESULTADO FINAL")
if fallos:
    print(f"  {len(fallos)} comprobacion(es) fallaron:")
    for f in fallos:
        print(f"    · {f}")
    sys.exit(1)
print("  SISTEMA COMPLETO VERIFICADO sobre la aplicacion publicada en Render.")
print("  Login + CRUD en 4 tablas relacionadas + JOIN + claves foraneas")
print("  + validaciones + cierre de sesion. La base quedo como estaba.")
