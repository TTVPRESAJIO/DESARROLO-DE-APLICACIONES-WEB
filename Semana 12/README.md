# Semana 12 · Persistencia de datos en un entorno local (SQLite)

Proyecto Integrador U3 · Avance 12/16
Desarrollo de Aplicaciones Web · Universidad Estatal Amazónica

---

## Qué cambió respecto a la Semana 11

En la Semana 11 los datos vivían en **listas de Python**: al cerrar la
aplicación se perdía todo. Esta semana la información se guarda en una
**base de datos SQLite local** y sobrevive al reinicio.

| | Semana 11 | Semana 12 |
|---|---|---|
| Dónde viven los datos | Listas en `app.py` | `data/electric_life.db` |
| Al reiniciar la aplicación | Todo vuelve al estado inicial | **Los registros siguen ahí** |
| Cómo se guarda | `lista.append()` | `INSERT INTO ... VALUES (?, ?)` |
| Cómo se lee | Recorrer la lista | `SELECT ... ` + `fetchall()` |

**Todo lo demás se conserva:** los formularios Flask-WTF, los validadores,
la `SECRET_KEY`, la protección CSRF, las plantillas, los componentes
reutilizables y los estilos.

---

## El flujo completo

```
Formulario  →  Validación      →  INSERT      →  SELECT      →  Jinja2
(WTForms)      validate_on_submit  en SQLite     fetchall()     tabla HTML
```

Nada se guarda si la validación falla: el `INSERT` está **dentro** del
`if form.validate_on_submit():`.

---

## Sobre el nombre de la base de datos

El enunciado y el material de clase proponen el nombre `ferreteria.db`
(diapositiva 18: *«La base puede vivir en data/ferreteria.db»*), porque el
ejemplo del docente es una ferretería.

En este proyecto el archivo se llama **`electric_life.db`**, adaptado al
tema del Proyecto Integrador (sistemas solares). Lo único que cambia es el
nombre del archivo: la ubicación (`data/`), la estructura de las tablas y
el funcionamiento son exactamente los que pide la actividad.

---

## Estructura

```
Semana 12/
├── app.py                  # Rutas: validan y llaman a la capa de datos
├── db.py                   # ⭐ NUEVO · toda la lógica de SQLite
├── requirements.txt
│
├── data/
│   └── electric_life.db    # ⭐ NUEVO · base de datos local
│
├── forms/                  # Sin cambios respecto a la Semana 11
│   ├── __init__.py
│   ├── producto_form.py
│   ├── cliente_form.py
│   ├── proveedor_form.py
│   ├── facturacion_form.py
│   └── portada_form.py
│
├── templates/              # Sin cambios
└── static/                 # Sin cambios
```

`db.py` concentra las consultas para no mezclar SQL con la lógica de las
rutas. Así, cuando en la Unidad 4 se pase a MySQL, solo habrá que cambiar
ese archivo.

---

## Las tablas

| Tabla | Qué guarda |
|---|---|
| `productos` | Catálogo de equipos solares |
| `clientes` | Clientes registrados |
| `proveedores` | Empresas que abastecen |
| `facturas` | Comprobantes emitidos |
| `solicitudes` | Solicitudes del formulario de la portada |
| `mensajes` | Mensajes del formulario de contacto |

Todas se crean con `CREATE TABLE IF NOT EXISTS`, de modo que volver a
ejecutar la aplicación **no borra** lo guardado. Los datos de ejemplo solo
se insertan la primera vez, cuando la tabla está vacía.

---

## Consultas parametrizadas

Todas las operaciones usan marcadores `?` en lugar de concatenar valores:

```python
cursor.execute(
    "INSERT INTO productos (nombre, categoria, precio, stock, icono) "
    "VALUES (?, ?, ?, ?, ?)",
    (nombre, categoria, precio, stock, icono))
conn.commit()
conn.close()
```

El valor viaja **aparte** de la instrucción SQL, así que nunca puede
interpretarse como código. Se comprobó registrando una solicitud cuyo
nombre era `Robert'); DROP TABLE productos;--`: se guardó como texto
literal y la tabla `productos` quedó intacta.

---

## Cómo ejecutarlo

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abre `http://127.0.0.1:5000`

La base de datos se crea sola en `data/electric_life.db` la primera vez.
**No necesita XAMPP ni ningún servidor externo**: SQLite es un solo archivo.

---

## Pruebas realizadas

1. **Formulario vacío** → los cuatro validadores muestran su mensaje y
   **no se ejecuta ningún INSERT**.
2. **Datos correctos** → se guarda, redirige al listado y confirma.
   Comprobado también abriendo el archivo `.db` directamente.
3. **Persistencia real** → se registró «Microinversor 800W», se cerró la
   aplicación por completo (puerto 5000 liberado), se volvió a ejecutar y
   el producto seguía ahí. Los datos de ejemplo **no se duplicaron**.
4. **Inyección SQL** → neutralizada por las consultas parametrizadas.
5. **Continuidad** → las rutas, formularios, validaciones, CSRF, plantillas
   y estilos de las semanas anteriores siguen funcionando, sin errores de
   consola.

---

## Nota sobre GitHub Pages

GitHub Pages solo publica contenido estático: no ejecuta Flask ni SQLite.
La publicación estática de las semanas anteriores se mantiene como
evidencia visual, y la persistencia se comprueba ejecutando el proyecto
localmente, tal como indica el enunciado.
