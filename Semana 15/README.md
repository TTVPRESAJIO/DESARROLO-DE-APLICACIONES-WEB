# Semana 15 · CRUD completo sobre PostgreSQL y despliegue en Render

Proyecto Integrador U4 · Avance 15/16
Desarrollo de Aplicaciones Web · Universidad Estatal Amazónica

---

## Qué cambió respecto a la Semana 14

Hasta ahora la aplicación funcionaba **solo en el computador**, contra un MySQL
levantado con XAMPP. Esta semana el proyecto da el salto a producción:

- La base de datos pasa de **MySQL a PostgreSQL**.
- La aplicación se **publica en Render**, con un PostgreSQL gestionado en la nube.
- Una sola variable, `DATABASE_URL`, configura la conexión en el servidor,
  y **el mismo código sigue corriendo en local** sin tocar nada.

**Todo lo anterior se conserva:** el login con contraseñas cifradas, las rutas
protegidas con `@login_required`, el modelo relacional con claves foráneas, las
consultas JOIN, los formularios validados con Flask-WTF, el CSRF, las plantillas
y los componentes reutilizables.

---

## De MySQL a PostgreSQL: qué hubo que cambiar de verdad

Migrar de un motor a otro suena más grande de lo que fue. Estos son **todos**
los cambios reales:

| Tema | MySQL (Semanas 13-14) | PostgreSQL (Semana 15) |
|---|---|---|
| Conector | `mysql-connector-python` | `psycopg2` |
| Marcador de parámetros | `%s` | `%s` — **igual** |
| Filas como diccionario | `conn.cursor(dictionary=True)` | `cursor_factory=RealDictCursor` |
| Id recién insertado | `cursor.lastrowid` | `INSERT ... RETURNING id` |
| Clave primaria autoincremental | `INT AUTO_INCREMENT` | `SERIAL` |
| Lista de tablas | `SHOW TABLES` | consulta a `information_schema` |
| Valores cerrados | `ENUM('Activo','Inactivo')` | `VARCHAR` + `CHECK (... IN ...)` |
| Fecha y hora | `DATETIME` | `TIMESTAMP` |
| Motor de tablas | `ENGINE=InnoDB` | no existe: las FK funcionan siempre |
| Crear la base | `CREATE DATABASE IF NOT EXISTS` | no existe esa forma: se consulta `pg_database` |

Lo más importante es la fila del medio: **el marcador de parámetros no cambia**.
Por eso las consultas parametrizadas de las semanas anteriores se mantuvieron
casi palabra por palabra, y la protección contra inyección SQL sigue intacta.

---

## El modelo relacional

Cuatro tablas relacionadas mediante **dos claves foráneas** (el enunciado pedía
un mínimo de tres tablas relacionadas):

```
  proveedores                          clientes
  ───────────                          ────────
  id_proveedor (PK)                    id_cliente (PK)
       ▲                                    ▲
       │ fk_producto_proveedor              │ fk_factura_cliente
       │ ON DELETE SET NULL                 │ ON DELETE RESTRICT
       │                                    │
  productos                            facturas
  ─────────                            ────────
  id_producto (PK)                     id_factura (PK)
  id_proveedor (FK)                    id_cliente (FK)
```

Las dos claves foráneas se comportan **distinto a propósito**, y eso se nota al
usar la aplicación:

- **`ON DELETE SET NULL`** — si borras un proveedor, sus productos no se pierden:
  quedan sin proveedor asignado. Por eso el listado usa `LEFT JOIN` y no
  `INNER JOIN`, para que esos productos sigan apareciendo.
- **`ON DELETE RESTRICT`** — no se puede borrar un cliente que ya tiene facturas.
  La aplicación lo comprueba antes y avisa en lenguaje llano, en vez de dejar que
  salte un error de la base.

Además están `solicitudes` y `mensajes` (formularios públicos de la portada) y
`usuarios` (autenticación), que suman **siete tablas** en total.

---

## Las cuatro operaciones CRUD

Cada módulo administrativo implementa el ciclo completo. Tomando productos como
ejemplo:

| Operación | Ruta | SQL |
|---|---|---|
| **CREAR** | `/productos/nuevo` | `INSERT INTO productos (...) VALUES (%s, ...) RETURNING id_producto` |
| **LEER** | `/productos` | `SELECT ... FROM productos p LEFT JOIN proveedores pr ON ...` |
| **ACTUALIZAR** | `/productos/editar/<id>` | `UPDATE productos SET ... WHERE id_producto = %s` |
| **ELIMINAR** | `/productos/eliminar/<id>` | `DELETE FROM productos WHERE id_producto = %s` |

Lo mismo para `/clientes`, `/proveedores` y `/facturacion`.

**Todos los `UPDATE` y `DELETE` llevan `WHERE`**, sin excepción: sin esa cláusula
una sola operación arrasaría con la tabla entera.

---

## Las consultas JOIN

El enunciado pedía al menos una. Hay dos, y las dos se muestran en pantalla:

**Productos con su proveedor** (`datos.listar_productos`):

```sql
SELECT  p.id_producto AS id, p.nombre, p.categoria, p.precio,
        p.stock, p.icono, p.id_proveedor,
        pr.empresa AS proveedor
FROM productos p
LEFT JOIN proveedores pr ON pr.id_proveedor = p.id_proveedor
ORDER BY p.id_producto
```

**Facturas con su cliente** (`datos.listar_facturas`):

```sql
SELECT  f.id_factura AS id, f.numero, f.fecha, f.total,
        f.estado, f.id_cliente,
        c.nombre AS cliente
FROM facturas f
INNER JOIN clientes c ON c.id_cliente = f.id_cliente
ORDER BY f.id_factura
```

En las tablas HTML esto se ve como una columna **Proveedor** y una columna
**Cliente** que no están en la tabla consultada: vienen de la tabla relacionada.

---

## Estructura

```
Semana 15/
├── app.py                  # Rutas, LoginManager y arranque
├── models.py               # Usuario (UserMixin) y consultas de autenticación
├── datos.py                # Capa de acceso a datos · CRUD sobre PostgreSQL
├── requirements.txt        # + psycopg2-binary y gunicorn
├── Procfile                ⭐ NUEVO · cómo arranca la app en Render
├── .env.example            ⭐ NUEVO · plantilla de variables (sin datos reales)
│
├── conexion/
│   └── conexion.py         # DATABASE_URL (Render) o parámetros sueltos (local)
│
├── sql/esquema.sql         # Modelo relacional en dialecto PostgreSQL
│
├── forms/                  # Sin cambios · validaciones de Flask-WTF
├── templates/              # Sin cambios salvo textos de MySQL → PostgreSQL
└── static/                 # Sin cambios
```

Y en la **raíz del repositorio**, `render.yaml`: Render busca ese archivo ahí, no
dentro de la subcarpeta, y desde él apunta a `Semana 15` con `rootDir`.

---

## Cómo se conecta la aplicación

Ésta es la pieza que hace que el mismo código sirva en los dos sitios:

```python
def get_db_connection():
    url = _config("DATABASE_URL")
    if url:
        # Render: la URL trae servidor, usuario, clave, puerto y base
        return psycopg2.connect(_normalizar_url(url))
    # Local: parámetros sueltos
    return psycopg2.connect(host=..., user=..., password=..., dbname=..., port=...)
```

Dos detalles que costaron pensarlos:

1. **Render entrega la URL empezando por `postgres://`**, una forma antigua.
   `_normalizar_url()` la convierte a `postgresql://`, que es la oficial.
2. **No se fuerza ningún `sslmode`.** psycopg2 usa por defecto `prefer`, que
   intenta cifrar y solo sigue sin cifrado si el servidor no lo admite. Así la
   misma línea sirve para la dirección interna de Render y para la externa, que
   sí exige SSL.

---

## Un detalle del despliegue que es fácil pasar por alto

En local la aplicación se lanza con `python app.py`, y la preparación de la base
vivía dentro de:

```python
if __name__ == "__main__":
    ...
```

**En Render eso no se ejecuta nunca.** Allí la aplicación la lanza gunicorn, que
*importa* `app.py` en lugar de ejecutarlo como programa principal. Si la creación
de las tablas se quedaba dentro de ese bloque, la base desplegada arrancaría
vacía y la aplicación fallaría al primer `SELECT`.

Por eso `preparar_base_de_datos()` se llama **fuera** del bloque, al importar el
módulo. Es idempotente (`CREATE TABLE IF NOT EXISTS`, y los datos de ejemplo solo
se insertan si la tabla está vacía), así que repetirlo no rompe nada.

---

## Pruebas realizadas

La secuencia que exige el enunciado —**Login → Listar → Agregar → Modificar →
Eliminar → consultar información relacionada → Cerrar sesión**— se comprobó
entera, verificando cada paso **también directamente en PostgreSQL**, no solo en
la pantalla:

| Paso | Qué se hizo | Resultado |
|---|---|---|
| **Login** | Entrar con `dallacuri` | ✅ *"Bienvenido, Daniel Allacuri Quilligana"* → `/dashboard` |
| **Listar** | Abrir `/productos` | ✅ 8 productos, cada uno con su proveedor (dato del JOIN) |
| **Agregar** | Registrar "Kit Solar Portatil 200W" | ✅ fila #9 creada; contador 8 → 9 |
| **Modificar** | Cambiar precio, stock y proveedor | ✅ 395,50 → 349,90 · stock 7 → 15 · Sunny Future → Proviento |
| **Eliminar** | Borrar ese producto | ✅ contador 9 → 8; las otras 8 filas intactas |
| **Relación** | Abrir `/facturacion` | ✅ columna **Cliente** traída con `INNER JOIN` |
| **Cerrar sesión** | `/logout` | ✅ *"Sesion cerrada"*; el menú de módulos desaparece |

**Comprobaciones adicionales:**

- **Contraseña cifrada.** En la tabla `usuarios` solo hay un hash de 162
  caracteres (`scrypt:32768:8:1$Tn5tLNbp0oPn9E80$...`). Buscando el texto plano
  en la columna: **0 filas**.
- **Contraseña incorrecta.** Devuelve *"Usuario o contrasena incorrectos"* y no
  abre sesión.
- **Validaciones intactas.** Enviar el formulario vacío responde *"No se pudo
  guardar. Revisa los 4 campo(s) marcados en rojo"* y no inserta nada.
- **Rutas protegidas.** Las 10 rutas administrativas devuelven `302 → /login`
  sin sesión, y `200` con ella. Las 3 públicas (`/`, `/login`, `/registro`)
  siguen abiertas.
- **Integridad referencial.** Intentar borrar "Farmacia Su Salud", que tiene
  facturas, se impide con un aviso en lenguaje llano (la FK es `ON DELETE
  RESTRICT`).
- **Inyección SQL.** Se guardó `Robert'); DROP TABLE productos;--` como nombre de
  proveedor: quedó almacenado **como texto literal** y la tabla `productos`
  siguió con sus 8 filas. Las consultas parametrizadas hacen su trabajo.
- **Sin errores** en la consola del navegador ni en el log del servidor.

---

## Despliegue en Render, paso a paso

1. Entra en [render.com](https://render.com) e inicia sesión con la cuenta de GitHub.
2. **New → Blueprint**.
3. Elige el repositorio `DESARROLO-DE-APLICACIONES-WEB`. Render detecta el
   `render.yaml` de la raíz.
4. Confirma. Render crea a la vez:
   - la base de datos PostgreSQL `electric-life-db`
   - el servicio web `electric-life`
   - la variable `DATABASE_URL`, que conecta los dos
   - la variable `SECRET_KEY`, con un valor aleatorio que genera Render
5. Espera a que el build termine (unos minutos la primera vez).
6. Abre la URL pública, entra a `/registro` y crea tu usuario.

Las tablas y los datos de ejemplo se crean solos en el primer arranque.

> **Sobre el plan gratuito:** el servicio se duerme tras un rato sin visitas, así
> que la primera carga después de un tiempo puede tardar cerca de un minuto. No
> está roto: está despertando.

---

## Cómo ejecutarlo en local

1. Instala PostgreSQL y déjalo corriendo.
2. Copia `.env.example` a `.env` y pon ahí tu contraseña de PostgreSQL
   (ese archivo está en `.gitignore` y no llega a GitHub).
3. Instala las dependencias y ejecuta:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

4. Abre `http://127.0.0.1:5000/registro` y crea tu usuario.

La base `electric_life_web`, las tablas y los datos de ejemplo se crean solos en
el primer arranque.

---

## Seguridad

Lo que exigía el enunciado, y dónde está cumplido:

- **Sin contraseñas reales en el repositorio.** Todo sale de variables de
  entorno. `render.yaml` no contiene ni una credencial: `SECRET_KEY` la genera
  Render y los datos de la base los entrega el propio servicio de PostgreSQL.
- **Contraseñas nunca en texto plano.** `generate_password_hash()` al registrar,
  `check_password_hash()` al entrar. Las cadenas no se comparan directamente.
- **Consultas parametrizadas** en todas las operaciones: los valores viajan
  aparte del SQL, nunca concatenados.
- **`WHERE` obligatorio** en todos los `UPDATE` y `DELETE`.
- **Rutas administrativas protegidas** con `@login_required`.
- El mensaje de error del login es el mismo tanto si falla el usuario como la
  contraseña, para no revelar qué nombres de usuario existen.

---

## Nota sobre GitHub Pages

GitHub Pages solo publica contenido estático: no ejecuta Flask, ni PostgreSQL, ni
las sesiones. La publicación de las semanas anteriores se mantiene como evidencia
visual del frontend, y **la aplicación completa se comprueba en Render**, que es
lo que pide esta semana.
