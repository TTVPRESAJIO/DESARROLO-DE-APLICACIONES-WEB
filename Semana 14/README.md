# Semana 14 · Sistema de login funcional

Proyecto Integrador U4 · Avance 14/16
Desarrollo de Aplicaciones Web · Universidad Estatal Amazónica

---

## Qué cambió respecto a la Semana 13

Hasta ahora cualquiera que abriera la aplicación podía entrar a los módulos
administrativos y modificar la base de datos. Esta semana el proyecto
incorpora **autenticación de usuarios**: registro, contraseñas cifradas,
inicio de sesión, protección de rutas y cierre de sesión.

**Todo lo anterior se conserva:** la conexión a MySQL, el modelo relacional
con claves foráneas, el CRUD completo, los formularios Flask-WTF, los
validadores, CSRF, las plantillas y los componentes.

---

## El flujo de autenticación

```
Registro   →   Hash          →   Login          →   Sesión      →   Protección      →   Logout
formulario     generate_         check_password_    login_user()    @login_required     logout_user()
               password_hash     hash
```

---

## La tabla `usuarios`

```sql
CREATE TABLE IF NOT EXISTS usuarios (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    usuario         VARCHAR(50)  NOT NULL UNIQUE,
    nombre_completo VARCHAR(120) NOT NULL,
    password        VARCHAR(255) NOT NULL,
    fecha_registro  DATETIME     NOT NULL
) ENGINE=InnoDB;
```

- **`usuario` es UNIQUE**: impide registrar dos veces el mismo nombre.
  La aplicación además avisa antes, en lenguaje llano, en vez de dejar que
  salte un error de la base.
- **`password` es VARCHAR(255)**: guarda el *hash*, que ocupa mucho más que
  una contraseña normal. Nunca se guarda la contraseña en texto plano.

---

## Cómo se protegen las contraseñas

Al registrar un usuario, `generate_password_hash()` transforma la contraseña
en un hash irreversible antes del `INSERT`:

```
scrypt:32768:8:1$k06lWGRSTbnY1Ujy$628c0df01ebf63cde62ce917bebfc52b...
```

Al iniciar sesión **no se comparan las cadenas**: `check_password_hash()`
vuelve a aplicar el mismo algoritmo a lo que el usuario escribió y compara
los resultados. Por eso ni siquiera quien tenga acceso a la base de datos
puede leer las contraseñas.

---

## Estructura

```
Semana 14/
├── app.py                  # + LoginManager, load_user y rutas de autenticación
├── models.py               ⭐ NUEVO · clase Usuario (UserMixin) y consultas
├── datos.py                # Sin cambios
├── requirements.txt        # + Flask-Login
│
├── conexion/               # Sin cambios
├── sql/esquema.sql         # + tabla usuarios
│
├── forms/
│   ├── login_form.py       ⭐ NUEVO
│   ├── usuario_form.py     ⭐ NUEVO
│   └── (los cuatro de los módulos, sin cambios)
│
├── templates/
│   ├── login.html          ⭐ NUEVO
│   ├── registro.html       ⭐ NUEVO
│   ├── dashboard.html      ⭐ NUEVO · panel del usuario autenticado
│   └── components/navbar.html   # + usuario actual y cerrar sesión
│
└── static/                 # Sin cambios
```

---

## Rutas

| Ruta | Acceso | Qué hace |
|---|---|---|
| `/` | Pública | Portada informativa |
| `/registro` | Pública | Crear una cuenta |
| `/login` | Pública | Iniciar sesión |
| `/dashboard` | 🔒 Protegida | Panel del usuario autenticado |
| `/logout` | 🔒 Protegida | Cerrar sesión |
| `/productos`, `/clientes`, `/proveedores`, `/facturacion` | 🔒 Protegidas | Módulos administrativos (y sus rutas de crear, editar y eliminar) |
| `/test_db` | 🔒 Protegida | Comprobación de la conexión |

**20 decoradores `@login_required`** protegen las rutas administrativas.
La configuración `login_manager.login_view = "login"` redirige automáticamente
a quien intente entrar sin sesión, conservando el destino en `?next=`.

---

## Pruebas obligatorias realizadas

Las diez comprobaciones que exige el enunciado:

| # | Prueba | Resultado |
|---|---|---|
| 1 | Registrar un usuario | ✅ `dallacuri` creado desde el formulario |
| 2 | Comprobar en MySQL | ✅ `id 1, dallacuri, Daniel Allacuri Quilligana` |
| 3 | La contraseña no está en texto plano | ✅ solo el hash `scrypt:32768:8:1$...` |
| 4 | Contraseña incorrecta | ✅ *"Usuario o contrasena incorrectos"*, sin abrir sesión |
| 5 | Credenciales correctas | ✅ *"Bienvenido, Daniel Allacuri Quilligana"* |
| 6 | Acceder a páginas protegidas | ✅ las 5 rutas responden 200 |
| 7 | Se muestra el usuario autenticado | ✅ en el navbar y en el panel (`current_user`) |
| 8 | Cerrar sesión | ✅ redirige al login y el menú desaparece |
| 9 | Entrar a una ruta protegida tras salir | ✅ probado con `/productos`, `/dashboard`, `/facturacion` |
| 10 | Redirige al login | ✅ `/login?next=%2Fproductos` |

**Extra comprobado:** al intentar registrar `dallacuri` por segunda vez, la
aplicación lo impide y la base sigue con **1 usuario** (la columna es UNIQUE).
El CRUD de la Semana 13 sigue funcionando: 9 productos tras autenticarse.

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

3. Abre `http://127.0.0.1:5000/registro` y crea tu usuario.
4. Inicia sesión en `http://127.0.0.1:5000/login`.

La tabla `usuarios` se crea sola al arrancar, junto al resto del esquema.

> **Nota:** el usuario de prueba `dallacuri` existe en la base local, pero su
> contraseña no está en el repositorio (solo el hash vive en MySQL, y la base
> no se sube). Crea tu propia cuenta desde `/registro`.

---

## Seguridad

- `SECRET_KEY` firma la cookie de sesión de Flask-Login y el token CSRF.
  Se lee de una variable de entorno, con un valor por defecto solo para
  desarrollo local.
- Las credenciales de MySQL también se leen de variables de entorno: **no hay
  contraseñas reales en el repositorio**.
- Todas las consultas siguen siendo parametrizadas con `%s`.
- El mensaje de error del login es el mismo tanto si falla el usuario como la
  contraseña, para no revelar qué nombres de usuario existen.

---

## Nota sobre GitHub Pages

GitHub Pages solo publica contenido estático: no ejecuta Flask, ni las
sesiones, ni MySQL. La publicación de las semanas anteriores se mantiene como
evidencia visual, y el sistema de login se comprueba ejecutando el proyecto
localmente, tal como indica el enunciado.
