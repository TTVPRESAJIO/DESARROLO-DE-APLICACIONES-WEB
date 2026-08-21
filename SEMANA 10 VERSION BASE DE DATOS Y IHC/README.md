# Semana 10 · Versión con base de datos e IHC

> **Esta carpeta tampoco es la entrega de la Semana 10.**
> La entrega es [`Semana 10`](../Semana%2010). Ésta es la **versión más
> completa del proyecto**: reúne el trabajo de tres asignaturas en una sola
> aplicación.

---

## La idea

El negocio **Electric Life** aparece en tres materias distintas, y en cada una
se construyó una pieza:

| Asignatura | Qué se construyó |
|---|---|
| **Desarrollo de Aplicaciones Web** | La aplicación Flask: rutas, plantillas Jinja2, herencia y componentes |
| **Bases de Datos** | La base relacional `electric_life` (MariaDB, 16 tablas en 3FN, vistas y procedimientos) |
| **Interacción Humano-Computador** | Un sitio en WordPress con tema propio, evaluado con las heurísticas de Nielsen y WCAG 2.1 |

Las tres piezas describían el mismo negocio pero vivían separadas. Esta
carpeta responde a la pregunta:

> **¿Y si fueran una sola cosa?**

El resultado es la aplicación Flask con los datos reales de la base de datos
y la capa de usabilidad y accesibilidad desarrollada en IHC.

---

## Qué aporta cada asignatura

### De Desarrollo Web
La estructura completa: `base.html`, componentes reutilizables con
`{% include %}`, la macro `badge_estado()`, `url_for()` para enlaces y
recursos, bucles y condicionales.

### De Bases de Datos
Los datos ya no son listas de Python. Salen de MariaDB:

- **Productos** → tabla `producto` + `categoria_producto`
- **Stock** → vista `vista_stock_producto` (calculado del Kardex, no guardado)
- **Clientes** y **Proveedores** → sus tablas
- **Facturación** → `venta` → `cotizacion` → `cliente`

### De IHC
Toda la capa de usabilidad, con su justificación documentada:

| Componente | Principio que implementa |
|---|---|
| Enlace "Saltar al contenido" (al pulsar Tab) | WCAG 2.4.1 · Evitar bloques |
| Panel A+ / alto contraste, con memoria | N7 · Flexibilidad · WCAG 1.4.3 y 1.4.4 |
| Barra de progreso de lectura | N1 · Visibilidad del estado |
| Región viva (anuncios por voz) | WCAG 4.1.3 · Mensajes de estado |
| Botón de WhatsApp | N2 · Correspondencia con el mundo real |
| Botón de volver arriba | N3 · Control y libertad |
| Ver servicios en tarjetas **o** en tabla | N7 · Flexibilidad de uso |
| Modal que cierra con Escape y devuelve el foco | N3 · WCAG 2.1.2 |
| Textos de ayuda, ejemplos y contador de caracteres | N5 · Prevención de errores |
| Video y mapa que **no cargan sin permiso** | N3 · Ética de interfaces |
| Transcripción del video | WCAG 1.2.1 · Alternativa textual |
| Campo trampa en lugar de captcha | N5 · El captcha es barrera de accesibilidad |
| Página 404 en lenguaje llano con salidas | N9 · Recuperación de errores |
| Migas de pan | N1 y N6 · Saber dónde estás |

---

## Lo que esta versión hace y ninguna otra hace

**Los formularios guardan de verdad en la base de datos.**

Hasta ahora el formulario de solicitudes sólo creaba tarjetas en el navegador:
al recargar la página, desaparecían. Aquí la solicitud se guarda, devuelve un
**número de caso** y sigue estando al volver.

Para lograrlo se añadieron **dos tablas propias del sitio web**:

| Tabla nueva | Guarda |
|---|---|
| `solicitud_web` | Las solicitudes del formulario de la portada |
| `mensaje_web` | Los mensajes del formulario de contacto |

> Estas tablas se crean solas la primera vez que se ejecuta la aplicación.
> **Las 16 tablas del diseño original de Bases de Datos no se tocan.**

Además, la validación ya no vive sólo en el navegador:

- **Validación en el servidor**: funciona aunque se desactive JavaScript.
  La del navegador es una comodidad; la del servidor es la que protege los datos.
- **Campo trampa (honeypot)**: invisible para las personas, atractivo para los
  robots. Si viene relleno, la solicitud se descarta sin guardarse.

---

## Diferencias con la entrega de la Semana 10

| | `Semana 10` (entrega) | Esta versión |
|---|---|---|
| Origen de los datos | Listas en `app.py` | MariaDB |
| Al recargar la página | Todo vuelve al inicio | Los datos siguen ahí |
| Validación | Sólo navegador | Navegador **y** servidor |
| Protección anti-robots | Ninguna | Campo trampa |
| El stock | Número escrito a mano | Calculado del Kardex |
| Accesibilidad | Estándar de Bootstrap | Capa IHC completa (WCAG 2.1 AA) |
| Página 404 | La de Flask | Propia, en lenguaje llano |
| Necesita XAMPP | No | **Sí** |

---

## Cómo ejecutarla

Necesita **XAMPP encendido** (basta con MySQL).

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

Las tablas `solicitud_web` y `mensaje_web` se crean automáticamente al
arrancar. Si tu MySQL usa otra contraseña o puerto, edita las variables
`DB_*` al inicio de `app.py`.

---

## Qué probar para ver la diferencia

1. **Pulsa Tab** nada más cargar la página: aparece "Saltar al contenido".
2. Usa los botones **A+** y **contraste** del borde izquierdo, recarga y
   comprueba que se mantienen.
3. Registra una solicitud, **recarga la página**: sigue ahí, con su número de caso.
4. Cambia entre **Tarjetas** y **Tabla comparativa** en Servicios.
5. Escribe una dirección inventada (`/loquesea`) para ver la página 404.
6. Fíjate en que el **video y el mapa no cargan** hasta que los autorices.

---

## Qué falta (semanas 11 en adelante)

- CRUD completo: hoy sólo se lee y se registran solicitudes; falta editar y eliminar.
- Formularios de alta y edición para productos, clientes y proveedores.
- Un panel de administración para consultar las solicitudes recibidas.
- Manejo elegante del caso en que XAMPP esté apagado.
