# Semana 11 · Validación de formularios con Flask-WTF

Proyecto Integrador U3 · Avance 11/16
Desarrollo de Aplicaciones Web · Universidad Estatal Amazónica

---

## Nota sobre el cambio de aspecto

**Se tomó la decisión de cambiar únicamente el aspecto visual de esta entrega.**

La interfaz que traía el proyecto desde la Semana 10 era funcional pero muy
sobria. Para esta semana se le aplicó la **capa de Interacción Humano-Computador**
desarrollada en la asignatura *Interacción Humano-Computador* (tema propio
`electric-life-ihc`), que ya estaba probada y evaluada con las heurísticas de
Nielsen y los criterios WCAG 2.1.

> **Lo único que cambió es cómo se ve y cómo se usa el sitio.**
> Toda la lógica, la estructura y los requisitos de la Semana 11 siguen siendo
> exactamente los mismos: los mismos formularios, los mismos validadores, las
> mismas rutas y la misma organización de carpetas.

### Qué cambió (solo presentación)

| Elemento | Antes | Ahora |
|---|---|---|
| `static/css/style.css` | Estilos básicos | Identidad visual completa + capa IHC |
| `static/js/script.js` | Script mínimo | Servicios dinámicos, modal, contadores, accesibilidad |
| `templates/base.html` | Estructura simple | + enlace de salto, barra de progreso, región viva, panel de accesibilidad, migas de pan |
| `templates/index.html` | Portada con 3 tarjetas | Portada completa: hero, nosotros, servicios, solicitudes y contacto |
| `templates/404.html` | No existía | Página de error en lenguaje llano |

### Qué NO cambió (todo lo evaluable)

- La carpeta `forms/` y sus clases.
- Los validadores de cada campo.
- Las rutas GET y POST de los cuatro módulos.
- `SECRET_KEY`, `form.hidden_tag()` y `form.validate_on_submit()`.
- La herencia de plantillas y los componentes reutilizables.
- La ausencia de base de datos: los datos siguen en estructuras de Python.

---

## Añadidos de accesibilidad y usabilidad

Como consecuencia del cambio visual, el proyecto gana:

| Componente | Principio que implementa |
|---|---|
| Enlace «Saltar al contenido» (al pulsar Tab) | WCAG 2.4.1 · Evitar bloques |
| Panel A+ / alto contraste, con memoria | N7 · Flexibilidad · WCAG 1.4.3 y 1.4.4 |
| Barra de progreso de lectura | N1 · Visibilidad del estado |
| Región viva (anuncios por voz) | WCAG 4.1.3 · Mensajes de estado |
| Botón de WhatsApp y de volver arriba | N2 y N3 |
| Servicios en tarjetas **o** en tabla | N7 · Flexibilidad de uso |
| Contador de caracteres y textos de ayuda | N1 y N5 · Prevención de errores |
| Migas de pan en las páginas internas | N1 y N6 · Saber dónde estás |
| Página 404 con salidas claras | N9 · Recuperación de errores |

---

## Lo que evidencia esta entrega (Semana 11)

### Organización de formularios

```
forms/
├── __init__.py
├── producto_form.py       → ProductoForm
├── cliente_form.py        → ClienteForm
├── proveedor_form.py      → ProveedorForm
├── facturacion_form.py    → FacturaForm
└── portada_form.py        → SolicitudForm y ContactoForm
```

Las seis clases heredan de `FlaskForm`.

> `portada_form.py` es un añadido de esta entrega: al cambiar la portada, sus
> dos formularios públicos también se pasaron a Flask-WTF. Así **todos** los
> formularios del proyecto quedan validados en el servidor y protegidos con CSRF,
> no solo los de los módulos internos.

### Validadores utilizados

| Validador | Dónde se usa |
|---|---|
| `DataRequired()` | Todos los campos obligatorios |
| `InputRequired()` | Precio y stock (un stock de 0 es válido y `DataRequired` lo rechazaría) |
| `Length()` | Nombres, teléfonos, cédula, descripciones |
| `Email()` | Correos de clientes, proveedores y contacto |
| `NumberRange()` | Precio, stock y total de la factura |
| `Regexp()` | Cédula (solo dígitos) y número de factura del SRI |
| Validador propio `validate_fecha()` | Impide emitir una factura con fecha futura |

### Protección CSRF

- `SECRET_KEY` configurada en `app.py`.
- `form.hidden_tag()` presente en las seis plantillas de formulario.
- Comprobado: un `POST` sin token **no guarda nada**.

### Reutilización

- Una sola clase por módulo sirve para **registrar y editar**: al editar se crea
  el formulario con `data=registro` y WTForms rellena los campos.
- Un solo macro `campo()` en `templates/components/campos.html` pinta la
  etiqueta, el campo y los mensajes de error de todos los formularios.

---

## Rutas

| Ruta | Métodos | Qué hace |
|---|---|---|
| `/` | GET, POST | Portada + formularios de solicitud y contacto |
| `/productos` | GET | Listado |
| `/productos/nuevo` | GET, POST | Registrar |
| `/productos/editar/<id>` | GET, POST | Editar |
| `/productos/eliminar/<id>` | POST | Eliminar |

Los módulos de clientes, proveedores y facturación siguen el mismo patrón.

---

## Cómo ejecutarlo

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abre `http://127.0.0.1:5000`

**No necesita base de datos ni XAMPP.** Los datos viven en memoria mientras la
aplicación está en ejecución, tal como pide la actividad de esta semana.

---

## Pruebas realizadas

1. **Campos vacíos** → mensajes bajo cada campo, nada se guarda.
2. **Valores inválidos** (nombre de 2 letras, precio 0, stock negativo, correo
   mal formado, cédula con letras, factura con fecha futura) → cada validador
   muestra su mensaje y no se pierde lo escrito.
3. **Datos correctos** → se guarda, redirige al listado y muestra la confirmación.
4. **POST sin token CSRF** → rechazado, no se guarda.
