# Semana 10 · Prueba con base de datos

> **Esta carpeta no es la entrega de la Semana 10.**
> La entrega es la carpeta [`Semana 10`](../Semana%2010), que cumple la actividad
> tal como está enunciada. Ésta es una **prueba de integración** que adelanta
> trabajo de las semanas siguientes.

---

## Por qué existe esta carpeta

La actividad de la Semana 10 pide expresamente que los datos se definan
en Python, sin base de datos:

> *"En esta semana no se requiere base de datos; los datos serán definidos
> temporalmente en Python."*

Al mismo tiempo, en la asignatura de **Bases de Datos** ya está terminada la
base relacional `electric_life` (MariaDB, 16 tablas normalizadas a 3FN) para
este mismo negocio. Tener dos veces la misma información —una en listas de
Python y otra en tablas— no tiene sentido a largo plazo.

Esta carpeta responde a una pregunta concreta:

> **¿Qué habría que cambiar en el proyecto Flask para que los datos salgan
> de la base real en lugar de las listas de Python?**

La respuesta resultó ser: **muy poco**. Y ése es justamente el hallazgo.

---

## Qué cambia respecto a la entrega

Sólo cambian dos cosas:

| Archivo | Qué cambia |
|---|---|
| `app.py` | Las listas de diccionarios se sustituyen por **modelos** y **consultas** |
| Los 4 módulos | Cambian los nombres de los campos (`nombre_modelo` en lugar de `nombre`) |

**Todo lo demás es idéntico**: `base.html`, `navbar.html`, `footer.html`,
`macros.html`, el CSS, el JavaScript y la página de inicio.

Los bucles `{% for %}` y las condiciones `{% if %}` de las plantillas
**siguen funcionando sin tocarlos**, porque reciben una colección de objetos
con las mismas propiedades. Ése es el beneficio real de haber separado bien
las plantillas en las semanas 7 a 10.

### Antes y después

```python
# ANTES (entrega): lista escrita a mano
def productos():
    return render_template("productos.html", productos=productos_data)

# DESPUÉS: consulta a MariaDB
def productos():
    filas = db.session.execute(text("SELECT ... FROM producto ...")).mappings().all()
    return render_template("productos.html", productos=filas)
```

---

## El detalle más interesante: el stock

En la base de datos **el stock no está guardado en ninguna columna**. Se
calcula sumando entradas y restando salidas del inventario (el Kardex),
mediante la vista `vista_stock_producto`.

Eso significa que si mañana se registra una compra en la base, la web lo
refleja sola, sin tocar una línea de código.

| Producto | Stock que muestra la web | Lo que dice la vista SQL |
|---|---|---|
| Panel monocristalino 450W | Disponible (4) | 4 |
| Los otros 6 | Agotado | 0 |

---

## Correspondencia módulo ↔ tabla

| Módulo web | Tabla(s) de `electric_life` |
|---|---|
| Productos | `producto` + `categoria_producto` + vista `vista_stock_producto` |
| Clientes | `cliente` |
| Proveedores | `proveedor` |
| Facturación | `venta` → `cotizacion` → `cliente` |

---

## Cómo ejecutarla

Necesita **XAMPP encendido** (Apache no hace falta, MySQL sí).

1. Enciende **MySQL** en el panel de XAMPP.
2. En phpMyAdmin: *Importar* → `electric_life_completo.sql` → *Continuar*.
3. Luego:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

4. Abre `http://127.0.0.1:5000`

Si tu MySQL usa otra contraseña o puerto, edita las variables `DB_*` al
inicio de `app.py`.

> ⚠️ Si XAMPP está apagado, esta versión **falla**. La carpeta `Semana 10`
> funciona siempre, porque no depende de nada externo.

---

## Limitaciones conocidas

- Sólo **lee** de la base (la R de CRUD). Todavía no crea, edita ni borra.
- El formulario de solicitudes sigue guardando sólo en el navegador.
  Eso se resuelve en la carpeta
  [`SEMANA 10 VERSION BASE DE DATOS Y IHC`](../SEMANA%2010%20VERSION%20BASE%20DE%20DATOS%20Y%20IHC).
