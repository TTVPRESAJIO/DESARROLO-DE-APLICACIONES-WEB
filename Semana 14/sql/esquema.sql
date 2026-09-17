-- =====================================================================
--  ELECTRIC LIFE · esquema.sql  (Semana 13)
--  ---------------------------------------------------------------------
--  Modelo relacional del Proyecto Integrador sobre MySQL / MariaDB.
--
--  Este archivo permite recrear la estructura completa de la base de
--  datos desde cero. Se ejecuta con:
--
--      mysql -u root -p < sql/esquema.sql
--
--  o importandolo desde phpMyAdmin.
--
--  RELACIONES (claves foraneas):
--     productos.id_proveedor  ->  proveedores.id_proveedor
--     facturas.id_cliente     ->  clientes.id_cliente
-- =====================================================================

CREATE DATABASE IF NOT EXISTS electric_life_web
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE electric_life_web;


-- ---------------------------------------------------------------------
--  PROVEEDORES  (tabla "padre" de productos)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS proveedores (
    id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    empresa      VARCHAR(100) NOT NULL,
    contacto     VARCHAR(80)  NOT NULL,
    correo       VARCHAR(100) NOT NULL,
    telefono     VARCHAR(15)  NOT NULL,
    ciudad       VARCHAR(60)  NOT NULL,
    suministra   VARCHAR(200) NOT NULL
) ENGINE=InnoDB;


-- ---------------------------------------------------------------------
--  CLIENTES  (tabla "padre" de facturas)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre     VARCHAR(120) NOT NULL,
    cedula     VARCHAR(13)  NOT NULL,
    correo     VARCHAR(100) NOT NULL,
    telefono   VARCHAR(15)  NOT NULL,
    ciudad     VARCHAR(60)  NOT NULL,
    estado     ENUM('Activo','Inactivo') NOT NULL DEFAULT 'Activo'
) ENGINE=InnoDB;


-- ---------------------------------------------------------------------
--  PRODUCTOS
--  Cada producto puede pertenecer a un proveedor (clave foranea).
--  ON DELETE SET NULL: si se elimina el proveedor, el producto no se
--  borra; simplemente se queda sin proveedor asignado.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS productos (
    id_producto  INT AUTO_INCREMENT PRIMARY KEY,
    nombre       VARCHAR(120)   NOT NULL,
    categoria    VARCHAR(60)    NOT NULL,
    precio       DECIMAL(10,2)  NOT NULL,
    stock        INT            NOT NULL DEFAULT 0,
    icono        VARCHAR(40),
    id_proveedor INT NULL,
    CONSTRAINT fk_producto_proveedor
        FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;


-- ---------------------------------------------------------------------
--  FACTURAS
--  Cada factura pertenece a un cliente (clave foranea).
--  ON DELETE RESTRICT: no se puede borrar un cliente que ya tiene
--  facturas emitidas, para no dejar comprobantes huerfanos.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS facturas (
    id_factura INT AUTO_INCREMENT PRIMARY KEY,
    numero     VARCHAR(20)   NOT NULL,
    id_cliente INT           NOT NULL,
    fecha      DATE          NOT NULL,
    total      DECIMAL(10,2) NOT NULL,
    estado     ENUM('Pagada','Pendiente','Anulada') NOT NULL DEFAULT 'Pendiente',
    CONSTRAINT fk_factura_cliente
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;


-- ---------------------------------------------------------------------
--  SOLICITUDES Y MENSAJES  (formularios publicos de la portada)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS solicitudes (
    id_solicitud INT AUTO_INCREMENT PRIMARY KEY,
    nombre       VARCHAR(80)  NOT NULL,
    categoria    VARCHAR(40)  NOT NULL,
    descripcion  TEXT         NOT NULL,
    fecha        DATETIME     NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS mensajes (
    id_mensaje INT AUTO_INCREMENT PRIMARY KEY,
    nombre     VARCHAR(80)  NOT NULL,
    correo     VARCHAR(100) NOT NULL,
    asunto     VARCHAR(60)  NOT NULL,
    mensaje    TEXT         NOT NULL,
    fecha      DATETIME     NOT NULL
) ENGINE=InnoDB;


-- ---------------------------------------------------------------------
--  USUARIOS  (Semana 14 · sistema de autenticacion)
--
--  · usuario es UNIQUE: impide registrar dos veces el mismo nombre.
--  · password guarda el HASH generado por generate_password_hash(),
--    NUNCA la contrasena en texto plano. El hash de Werkzeug ocupa
--    bastante mas de 100 caracteres, por eso la columna es VARCHAR(255).
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    usuario         VARCHAR(50)  NOT NULL UNIQUE,
    nombre_completo VARCHAR(120) NOT NULL,
    password        VARCHAR(255) NOT NULL,
    fecha_registro  DATETIME     NOT NULL
) ENGINE=InnoDB;


-- =====================================================================
--  DATOS DE EJEMPLO
--  Se insertan primero los proveedores y clientes, porque productos y
--  facturas dependen de ellos a traves de las claves foraneas.
-- =====================================================================

INSERT INTO proveedores (empresa, contacto, correo, telefono, ciudad, suministra) VALUES
('Proviento',    'Ventas Proviento', 'ventas@proviento.com.ec', '022500000',  'Quito',    'Paneles, inversores y baterias'),
('Pintulac',     'Atencion Cliente', 'info@pintulac.com.ec',    '1800746852', 'Nacional', 'Paneles, inversores y baterias'),
('Sunny Future', 'Ventas SF',        'info@sunnyfuture.co',     '022600000',  'Quito',    'Baterias de litio e inversores'),
('Amawtec',      'Distribucion',     'ventas@amawtec.com',      '062600000',  'Ibarra',   'Kits fotovoltaicos Growatt');

INSERT INTO clientes (nombre, cedula, correo, telefono, ciudad, estado) VALUES
('Farmacia Su Salud',         '1690012345001', 'farmaciasusalud@gmail.com', '032885001',  'Puyo', 'Activo'),
('Ferreteria El Constructor', '1690023456001', 'elconstructor@gmail.com',   '032885002',  'Puyo', 'Activo'),
('Restaurante El Jardin',     '1690034567001', 'eljardinpuyo@gmail.com',    '032885003',  'Puyo', 'Inactivo'),
('Juan Andres Perez',         '1600456789',    'juanperez@gmail.com',       '0991112233', 'Puyo', 'Activo'),
('Cyber Amazonia',            '1690045678001', 'cyberamazonia@gmail.com',   '032885004',  'Puyo', 'Activo');

INSERT INTO productos (nombre, categoria, precio, stock, icono, id_proveedor) VALUES
('Panel Solar Monocristalino 450W', 'Panel Solar', 180.00, 24,  'bi-sun',                4),
('Inversor Hibrido 3kW',            'Inversor',    650.00, 8,   'bi-lightning-charge',   4),
('Bateria de Litio 100Ah',          'Bateria',     520.00, 12,  'bi-battery-full',       3),
('Regulador MPPT 60A',              'Regulador',   140.00, 15,  'bi-sliders',            1),
('Breaker DC 63A',                  'Proteccion',  25.00,  40,  'bi-shield-check',       2),
('Cable Fotovoltaico 6mm (metro)',  'Cableado',    2.50,   300, 'bi-plug',               2),
('Estructura de Montaje Aluminio',  'Estructura',  45.00,  0,   'bi-grid-3x3',           1),
('Controlador de Carga PWM 30A',    'Regulador',   60.00,  0,   'bi-sliders',            3);

INSERT INTO facturas (numero, id_cliente, fecha, total, estado) VALUES
('001-001-000001', 1, '2026-07-12', 2730.00, 'Pagada'),
('001-001-000002', 5, '2026-07-23', 1530.00, 'Pagada'),
('001-001-000003', 2, '2026-07-28', 890.00,  'Pendiente'),
('001-001-000004', 4, '2026-08-02', 420.00,  'Pendiente'),
('001-001-000005', 3, '2026-08-05', 310.00,  'Anulada');


-- =====================================================================
--  CONSULTA RELACIONADA DE EJEMPLO (JOIN entre dos tablas)
--  Muestra cada producto junto al nombre de su proveedor.
-- =====================================================================
-- SELECT p.id_producto, p.nombre, p.precio, pr.empresa AS proveedor
-- FROM productos p
-- LEFT JOIN proveedores pr ON pr.id_proveedor = p.id_proveedor
-- ORDER BY p.id_producto;
