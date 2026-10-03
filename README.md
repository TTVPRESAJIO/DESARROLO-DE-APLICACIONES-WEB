# Electric Life · Sistema web de gestión

**Proyecto Integrador — Desarrollo de Aplicaciones Web**
Universidad Estatal Amazónica · Puyo, Pastaza · 2026
Daniel Fernando Allacuri Quilligana

---

## 🔗 Aplicación en funcionamiento

| | |
|---|---|
| **Aplicación desplegada** | https://electric-life.onrender.com |
| **Proyecto final (código)** | [`Semana 15/`](Semana%2015) |
| **Frontend estático** | https://ttvpresajio.github.io/DESARROLO-DE-APLICACIONES-WEB/Semana%208/index%20SEMANA%208.html |

> La aplicación está en el plan gratuito de Render: si lleva un rato sin visitas
> se duerme, y **la primera carga puede tardar cerca de un minuto**. No está
> caída, está despertando.

---

## De qué trata

**Electric Life** es un negocio (ficticio) de Puyo que vende e instala sistemas
de respaldo solar: paneles, inversores, baterías e internet que no se corta
durante los apagones.

El sistema web tiene **dos caras**:

- **Una pública**, para los clientes: catálogo de servicios, formulario de
  solicitud de instalación y formulario de contacto.
- **Una privada**, para la empresa: panel de administración protegido por
  usuario y contraseña, donde se gestionan productos, clientes, proveedores y
  facturas.

---

## Qué incluye

| Requisito | Dónde está |
|---|---|
| **Autenticación de usuarios** | Registro, login con contraseña cifrada y cierre de sesión (Flask-Login) |
| **CRUD completo** | Crear, Leer, Actualizar y Eliminar en los 4 módulos administrativos |
| **Tablas relacionadas** | 7 tablas, 2 claves foráneas, consultas JOIN |
| **Rutas protegidas** | 20 decoradores `@login_required` |
| **Formularios validados** | Flask-WTF / WTForms, con protección CSRF |
| **Base de datos** | PostgreSQL, alojada en Render |
| **Despliegue** | Render, mediante el `render.yaml` de esta carpeta |

---

## El modelo de datos

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

Más `solicitudes` y `mensajes` (los formularios públicos de la portada) y
`usuarios` (autenticación): **siete tablas en total**.

Las dos claves foráneas se comportan distinto a propósito:

- **`ON DELETE SET NULL`** — si se borra un proveedor, sus productos no se
  pierden: quedan sin proveedor asignado.
- **`ON DELETE RESTRICT`** — no se puede borrar un cliente que ya tiene
  facturas emitidas. La aplicación lo avisa en lenguaje llano antes de que la
  base lance un error.

---

## Tecnologías

**Backend:** Python 3.12 · Flask · Jinja2 · Flask-WTF · Flask-Login · psycopg2
**Base de datos:** PostgreSQL
**Frontend:** HTML5 · CSS3 · Bootstrap 5.3 · JavaScript
**Despliegue:** Render (gunicorn) · GitHub

---

## Cómo ejecutarlo en tu computador

```bash
cd "Semana 15"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Necesitas **PostgreSQL** corriendo. Copia `.env.example` a `.env` y pon ahí tus
datos de acceso. La base, las tablas y los datos de ejemplo se crean solos en el
primer arranque.

Luego abre http://127.0.0.1:5000/registro y crea tu usuario.

---

## Cómo está organizado el repositorio

Cada carpeta es el avance de una semana. **El proyecto final es `Semana 15`**;
las anteriores se conservan como historial del proceso.

| Carpeta | Tema |
|---|---|
| `Semana 4` – `Semana 6` | Estructura HTML, estilos CSS y primeros scripts |
| `Semana 7` | Plantillas y renderizado dinámico con JavaScript |
| `Semana 8` | Componentes de Bootstrap |
| `Semana 9` | Flask y plantillas Jinja2 |
| `Semana 10` | Rutas y módulos administrativos (+ 2 versiones alternativas) |
| `Semana 11` | Validación de formularios con Flask-WTF |
| `Semana 12` | Persistencia local con SQLite |
| `Semana 13` | Base de datos relacional en MySQL |
| `Semana 14` | Sistema de login con contraseñas cifradas |
| **`Semana 15`** | **PostgreSQL + CRUD completo + despliegue en Render** |

Cada carpeta desde la Semana 11 tiene su propio `README.md` explicando qué se
hizo esa semana y por qué.

---

## Seguridad

- **No hay ninguna contraseña real en este repositorio.** Las credenciales de la
  base de datos y la clave de sesión se leen de variables de entorno; en Render
  las genera y guarda el propio servicio.
- **Las contraseñas de los usuarios nunca se guardan en texto plano.** Se
  almacena el hash de `generate_password_hash()` y se comprueba con
  `check_password_hash()`.
- **Todas las consultas SQL son parametrizadas**: los valores viajan aparte del
  SQL, nunca concatenados. Comprobado enviando `Robert'); DROP TABLE
  productos;--` como nombre: se guardó como texto literal y la tabla siguió
  intacta.
- **Todos los `UPDATE` y `DELETE` llevan `WHERE`.**
- **Protección CSRF** en todos los formularios.
