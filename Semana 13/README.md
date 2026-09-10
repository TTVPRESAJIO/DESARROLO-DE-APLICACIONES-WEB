# Semana 13 · Base de datos relacional (MySQL / MariaDB)

Proyecto Integrador U4 · Avance 13/16
Desarrollo de Aplicaciones Web · Universidad Estatal Amazónica

---

## Qué cambió respecto a la Semana 12

La Semana 12 guardaba los datos en un archivo SQLite local. Esta semana el
proyecto pasa a una **base de datos relacional MySQL/MariaDB**, con modelo
de tablas relacionadas mediante claves foráneas.

| | Semana 12 | Semana 13 |
|---|---|---|
| Motor | SQLite (archivo local) | **MySQL / MariaDB** (servidor) |
| Conexión | `sqlite3.connect()` | `mysql.connector.connect()` centralizado |
| Marcadores | `?` | `%s` |
| Relaciones | Ninguna | **2 claves foráneas** |
| Consultas | Sobre una tabla | **JOIN entre dos tablas** |

**Todo lo anterior se conserva:** formularios Flask-WTF, validadores,
`SECRET_KEY`, protección CSRF, plantillas, componentes reutilizables y estilos.

---

## Modelo relacional

```
proveedores                          clientes
├── id_proveedor (PK)                ├── id_cliente (PK)
├── empresa                          ├── nombre
├── contacto, correo, telefono       ├── cedula, correo, telefono
├── ciudad, suministra               ├── ciudad, estado
      ▲                                    ▲
      │ FK                                 │ FK
      │                                    │
productos                            facturas
├── id_producto (PK)                 ├── id_factura (PK)
├── nombre, categoria                ├── numero
├── precio, stock, icono             ├── fecha, total, estado
└── id_proveedor (FK) ────┘          └── id_cliente (FK) ─────┘
```

| Clave foránea | Comportamiento | Por qué |
|---|---|---|
| `productos.id_proveedor` → `proveedores` | `ON DELETE SET NULL` | Si se elimina un proveedor, sus productos no se borran: quedan sin proveedor asignado |
| `facturas.id_cliente` → `clientes` | `ON DELETE RESTRICT` | No se puede borrar un cliente con facturas emitidas, para no dejar comprobantes huérfanos |

La aplicación avisa en lenguaje llano cuando esto ocurre, en lugar de dejar
que salte un error de base de datos.

---

## Estructura

```
Semana 13/
├── app.py                  # Rutas: validan y llaman a la capa de datos
├── datos.py                # Consultas SQL (SELECT, INSERT, UPDATE, DELETE)
├── requirements.txt
│
├── conexion/               ⭐ NUEVO
│   ├── __init__.py
│   └── conexion.py         # get_db_connection() · punto único de conexión
│
├── sql/                    ⭐ NUEVO
│   └── esquema.sql         # CREATE DATABASE + CREATE TABLE + datos de ejemplo
│
├── forms/                  # Los de la Semana 11, con dos campos FK añadidos
├── templates/              # Las mismas plantillas + test_db.html
└── static/                 # Sin cambios
```

---

## Configuración de la conexión

Los datos de acceso se leen de **variables de entorno**, para no dejar
contraseñas reales escritas en el repositorio:

| Variable | Valor por defecto |
|---|---|
| `MYSQL_HOST` | `localhost` |
| `MYSQL_USER` | `root` |
| `MYSQL_PASSWORD` | *(vacía — XAMPP recién instalado)* |
| `MYSQL_DATABASE` | `electric_life_web` |
| `MYSQL_PORT` | `3306` |

Si tu MySQL usa contraseña, defínela antes de ejecutar:

```bash
set MYSQL_PASSWORD=tu_contrasena
python app.py
```

### Comprobar la conexión

La ruta **`/test_db`** muestra las tablas existentes, tal como sugiere el
material de clase. Si algo falla, explica qué revisar.

---

## Operaciones SQL evidenciadas

Todas usan **consultas parametrizadas** con `%s`: los valores viajan aparte
de la instrucción, nunca concatenados.

| Operación | Dónde | Consulta |
|---|---|---|
| **SELECT** | `datos.listar_productos()` | `SELECT ... FROM productos LEFT JOIN proveedores ...` |
| **INSERT** | `datos.crear_producto()` | `INSERT INTO productos (...) VALUES (%s, %s, ...)` |
| **UPDATE** | `datos.actualizar_producto()` | `UPDATE productos SET ... WHERE id_producto = %s` |
| **DELETE** | `datos.eliminar_producto()` | `DELETE FROM productos WHERE id_producto = %s` |
| **WHERE** | `datos.contar_clientes_activos()` | `SELECT COUNT(*) FROM clientes WHERE estado = %s` |
| **JOIN** | `datos.listar_facturas()` | `INNER JOIN clientes ON c.id_cliente = f.id_cliente` |

`UPDATE` y `DELETE` **siempre** llevan `WHERE`, y tras cada operación que
modifica datos se ejecuta `conn.commit()` y se cierran cursor y conexión.

---

## Cómo ejecutarlo

1. Enciende **MySQL** en el panel de XAMPP.
2. Instala las dependencias y ejecuta:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

3. Abre `http://127.0.0.1:5000/test_db` para confirmar la conexión.

La base y las tablas se crean solas la primera vez ejecutando
`sql/esquema.sql`. Como usa `IF NOT EXISTS`, volver a ejecutar la aplicación
**no borra** lo guardado, y los datos de ejemplo solo se insertan si la base
está vacía.

También puedes crear la estructura manualmente:

```bash
mysql -u root -p < sql/esquema.sql
```

---

## Pruebas obligatorias realizadas

Las diez comprobaciones que exige el enunciado, verificadas en la aplicación
**y** directamente en MySQL:

| # | Prueba | Resultado |
|---|---|---|
| 1 | Iniciar Flask y entrar al módulo | ✅ |
| 2 | El listado viene de MySQL | ✅ 8 productos con su proveedor (JOIN) |
| 3 | Agregar un registro por formulario | ✅ "Kit Solar Vivienda 5kW" |
| 4 | Comprobar el INSERT en la base | ✅ `id_producto 9, precio 1250.00, id_proveedor 3` |
| 5 | Modificar ese registro | ✅ precio → 1399.99, stock → 10, proveedor → Amawtec |
| 6 | Comprobar el UPDATE en la base | ✅ y solo cambió 1 de 9 filas (el `WHERE` funcionó) |
| 7 | Eliminar un registro | ✅ desde la interfaz, con confirmación |
| 8 | Comprobar el DELETE en la base | ✅ desapareció de la web y de MySQL |
| 9 | Cerrar y reiniciar Flask | ✅ puerto liberado y vuelto a levantar |
| 10 | Los cambios se mantienen | ✅ sin duplicar los datos de ejemplo |

**Extra comprobado:** al intentar eliminar un cliente con facturas, la
aplicación lo impide y muestra *"No se puede eliminar a «Farmacia Su Salud»:
tiene facturas emitidas"*. La integridad referencial funciona.

---

## Nota sobre GitHub Pages

GitHub Pages solo publica contenido estático: no ejecuta Flask ni MySQL. La
publicación de las semanas anteriores se mantiene como evidencia visual, y
las operaciones SELECT/INSERT/UPDATE/DELETE se comprueban ejecutando el
proyecto localmente, tal como indica el enunciado.

---

## Relación con la base de datos de la asignatura Bases de Datos

Este proyecto usa una base propia, **`electric_life_web`**, con el modelo que
pide esta actividad. La base `electric_life` (16 tablas, normalizada a 3FN)
desarrollada en la asignatura de Bases de Datos **queda intacta**: son dos
bases independientes en el mismo servidor MySQL.
