# Semana 16 · Pruebas finales del sistema

Proyecto Integrador · Evaluación final
Desarrollo de Aplicaciones Web · Universidad Estatal Amazónica

---

## Qué contiene esta carpeta

Esta semana **no añade código nuevo**: el sistema terminado es
[`Semana 15/`](../Semana%2015). Lo que hay aquí es la **evidencia de que
funciona**, que es lo que pide la evaluación final.

- `prueba_sistema.py` — la batería de pruebas automatizadas
- este `README.md` — los resultados

---

## Qué se probó y dónde

Las pruebas se ejecutaron **contra la aplicación publicada**, no contra una copia
local:

```
https://electric-life.onrender.com
```

**36 comprobaciones, 36 correctas.**

---

## Resultados

### 1 · Autenticación y protección de rutas

| Comprobación | Resultado |
|---|---|
| Sin sesión, `/productos` redirige al login | ✅ `302 → /login?next=%2Fproductos` |
| Contraseña incorrecta no abre sesión | ✅ |
| Usuario inexistente no abre sesión | ✅ |
| Credenciales correctas abren sesión | ✅ |
| Se muestra el usuario autenticado | ✅ |

> El mensaje de error es **idéntico** cuando falla el usuario y cuando falla la
> contraseña, para no revelar qué nombres de usuario existen.

### 2 · CRUD completo en cuatro tablas relacionadas

Cada módulo se probó entero: crear un registro, modificarlo, borrarlo y
comprobar que la tabla vuelve a su estado inicial.

| Módulo | Crear | Actualizar | Eliminar | Solo tocó su propia fila |
|---|:--:|:--:|:--:|:--:|
| **Productos** (hija de proveedores) | ✅ 8→9 | ✅ | ✅ 9→8 | ✅ |
| **Proveedores** (padre de productos) | ✅ 4→5 | ✅ | ✅ 5→4 | ✅ |
| **Clientes** (padre de facturas) | ✅ 5→6 | ✅ | ✅ 6→5 | ✅ |
| **Facturas** (hija de clientes) | ✅ 5→6 | ✅ | ✅ 6→5 | ✅ |

En cada actualización se verificó además que **el contador no sube**: un `UPDATE`
modifica, no crea. Y en cada borrado, que **las demás filas quedan intactas**:
el `DELETE` lleva `WHERE`.

### 3 · Relaciones entre tablas

| Comprobación | Resultado |
|---|---|
| JOIN productos–proveedores: cada producto muestra su proveedor | ✅ los 4 proveedores aparecen |
| Ningún producto quedó sin proveedor | ✅ |
| JOIN facturas–clientes: cada factura muestra su cliente | ✅ 4 clientes distintos |
| `ON DELETE RESTRICT`: no borra un cliente con facturas | ✅ avisa y no borra |
| El cliente sigue existiendo después del intento | ✅ |

### 4 · Validación de formularios

| Entrada rechazada | Resultado |
|---|---|
| Formulario vacío | ✅ |
| Precio negativo | ✅ |
| Correo con formato inválido | ✅ |
| Número de factura fuera del formato del SRI | ✅ |
| Factura con fecha futura | ✅ |

Ninguna de esas entradas llegó a la base de datos.

### 5 · Cierre de sesión

| Comprobación | Resultado |
|---|---|
| Cierra la sesión | ✅ |
| Tras salir, las rutas vuelven a estar protegidas | ✅ |

### 6 · La base quedó como estaba

| Tabla | Registros al terminar |
|---|---|
| productos | 8 ✅ |
| proveedores | 4 ✅ |
| clientes | 5 ✅ |
| facturas | 5 ✅ |

Sin restos de los datos de prueba.

---

## Cómo ejecutar las pruebas

Las credenciales **no están escritas en el archivo**: el repositorio es público.
Se pasan como variables de entorno.

```bash
set PRUEBA_USUARIO=tu_usuario
set PRUEBA_PASSWORD=tu_contrasena
python prueba_sistema.py
```

Para probar contra una instalación local en vez de Render:

```bash
set APP_URL=http://127.0.0.1:5000
```

---

## Una nota sobre cómo está escrita la prueba

La primera versión de este script tenía un defecto serio: para localizar el
registro que acababa de crear, buscaba su nombre dentro del HTML y deducía el
identificador del fragmento vecino. Cuando el alta fallaba por una validación,
esa deducción apuntaba a **otra fila** — y el script terminaba modificando y
borrando registros reales.

La versión definitiva no deduce nada: **compara la lista de identificadores antes
y después del alta**, y el identificador nuevo es la diferencia entre las dos.
Si el alta no se produjo, el bloque se detiene en vez de seguir adelante.

Es un recordatorio de algo que vale más que la prueba en sí: *un script que
escribe en una base de datos tiene que estar seguro de a qué fila le está
escribiendo.*
