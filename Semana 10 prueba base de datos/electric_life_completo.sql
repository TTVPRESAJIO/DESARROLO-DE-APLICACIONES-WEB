-- =====================================================================
--  ELECTRIC LIFE  ·  Base de datos para la gestion integral
--  Script DDL (Definicion de datos)  ·  Motor: MariaDB / MySQL (XAMPP)
--  Asignatura: Bases de Datos (UEA-L-UFPTI-001) · Unidad 4 - Normalizacion
--  Universidad Estatal Amazonica · Puyo, Pastaza
-- =====================================================================

DROP DATABASE IF EXISTS electric_life;
CREATE DATABASE electric_life
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE electric_life;

-- ---------------------------------------------------------------------
-- 1. CLIENTE
-- ---------------------------------------------------------------------
CREATE TABLE cliente (
    id_cliente          INT AUTO_INCREMENT PRIMARY KEY,
    tipo_cliente        ENUM('Hogar','Negocio') NOT NULL,
    nombre_razon_social VARCHAR(120) NOT NULL,
    ruc_cedula          VARCHAR(13) UNIQUE,
    telefono            VARCHAR(15),
    correo              VARCHAR(100),
    direccion           VARCHAR(200),
    ciudad              VARCHAR(60) DEFAULT 'Puyo',
    fecha_registro      DATE NOT NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 2. EMPLEADO (socios y su rol operativo)
-- ---------------------------------------------------------------------
CREATE TABLE empleado (
    id_empleado  INT AUTO_INCREMENT PRIMARY KEY,
    nombres      VARCHAR(80) NOT NULL,
    apellidos    VARCHAR(80) NOT NULL,
    cedula       VARCHAR(10) NOT NULL UNIQUE,
    rol          ENUM('Supervisor Tecnico','Compras y Logistica','Tecnico Instalador') NOT NULL,
    telefono     VARCHAR(15),
    correo       VARCHAR(100)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 3. PROVEEDOR
-- ---------------------------------------------------------------------
CREATE TABLE proveedor (
    id_proveedor         INT AUTO_INCREMENT PRIMARY KEY,
    nombre               VARCHAR(100) NOT NULL,
    ubicacion            VARCHAR(100),
    telefono             VARCHAR(15),
    correo               VARCHAR(100),
    suministro_principal VARCHAR(200)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 4. CATEGORIA_PRODUCTO (catalogo + clasificacion ABC)
-- ---------------------------------------------------------------------
CREATE TABLE categoria_producto (
    id_categoria      INT AUTO_INCREMENT PRIMARY KEY,
    nombre_categoria  VARCHAR(60) NOT NULL UNIQUE,
    clasificacion_abc ENUM('A','B','C') NOT NULL,
    descripcion       VARCHAR(150)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 5. PRODUCTO (paneles, inversores, baterias, accesorios)
-- ---------------------------------------------------------------------
CREATE TABLE producto (
    id_producto    INT AUTO_INCREMENT PRIMARY KEY,
    id_categoria   INT NOT NULL,
    id_proveedor   INT,
    nombre_modelo  VARCHAR(120) NOT NULL,
    marca          VARCHAR(60),
    precio_venta   DECIMAL(10,2) NOT NULL,
    garantia_meses INT DEFAULT 12,
    CONSTRAINT fk_producto_categoria FOREIGN KEY (id_categoria)
        REFERENCES categoria_producto(id_categoria)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_producto_proveedor FOREIGN KEY (id_proveedor)
        REFERENCES proveedor(id_proveedor)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 6. COTIZACION (cabecera de la cotizacion)
-- ---------------------------------------------------------------------
CREATE TABLE cotizacion (
    id_cotizacion INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente    INT NOT NULL,
    id_empleado   INT NOT NULL,
    fecha         DATE NOT NULL,
    estado        ENUM('Pendiente','Aprobada','Rechazada') NOT NULL DEFAULT 'Pendiente',
    total         DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    CONSTRAINT fk_cotizacion_cliente FOREIGN KEY (id_cliente)
        REFERENCES cliente(id_cliente) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_cotizacion_empleado FOREIGN KEY (id_empleado)
        REFERENCES empleado(id_empleado) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 7. DETALLE_COTIZACION (lineas - resuelve N:M)
-- ---------------------------------------------------------------------
CREATE TABLE detalle_cotizacion (
    id_detalle_cotizacion INT AUTO_INCREMENT PRIMARY KEY,
    id_cotizacion         INT NOT NULL,
    id_producto           INT NOT NULL,
    cantidad              INT NOT NULL,
    precio_unitario       DECIMAL(10,2) NOT NULL,
    CONSTRAINT uq_detalle_cotizacion UNIQUE (id_cotizacion, id_producto),
    CONSTRAINT fk_detcot_cotizacion FOREIGN KEY (id_cotizacion)
        REFERENCES cotizacion(id_cotizacion) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_detcot_producto FOREIGN KEY (id_producto)
        REFERENCES producto(id_producto) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 8. VENTA (nace de una cotizacion aprobada)  [RF-06]
-- ---------------------------------------------------------------------
CREATE TABLE venta (
    id_venta      INT AUTO_INCREMENT PRIMARY KEY,
    id_cotizacion INT NOT NULL UNIQUE,           -- 1:1 con la cotizacion aprobada
    id_empleado   INT NOT NULL,
    fecha_venta   DATE NOT NULL,
    forma_pago    ENUM('Efectivo','Transferencia','Tarjeta','Credito') NOT NULL DEFAULT 'Efectivo',
    total         DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    anticipo      DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    saldo         DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    CONSTRAINT fk_venta_cotizacion FOREIGN KEY (id_cotizacion)
        REFERENCES cotizacion(id_cotizacion) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_venta_empleado FOREIGN KEY (id_empleado)
        REFERENCES empleado(id_empleado) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 9. DIAGNOSTICO (informe de carga critica del cliente)
-- ---------------------------------------------------------------------
CREATE TABLE diagnostico (
    id_diagnostico      INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente          INT NOT NULL,
    fecha               DATE NOT NULL,
    consumo_estimado_wh DECIMAL(10,2),
    horas_respaldo      DECIMAL(5,2),
    cargas_criticas     TEXT,
    CONSTRAINT fk_diagnostico_cliente FOREIGN KEY (id_cliente)
        REFERENCES cliente(id_cliente) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 10. INSTALACION (ejecucion tecnica de una venta)  [RF-07]
-- ---------------------------------------------------------------------
CREATE TABLE instalacion (
    id_instalacion        INT AUTO_INCREMENT PRIMARY KEY,
    id_venta              INT NOT NULL UNIQUE,     -- 1:1 con la venta
    id_empleado           INT NOT NULL,
    id_diagnostico        INT,
    fecha_inicio          DATE,
    fecha_entrega         DATE,
    estado                ENUM('Programada','En instalacion','En pruebas','Entregado','Cancelado')
                          NOT NULL DEFAULT 'Programada',
    direccion_instalacion VARCHAR(200),
    CONSTRAINT fk_instalacion_venta FOREIGN KEY (id_venta)
        REFERENCES venta(id_venta) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_instalacion_empleado FOREIGN KEY (id_empleado)
        REFERENCES empleado(id_empleado) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_instalacion_diagnostico FOREIGN KEY (id_diagnostico)
        REFERENCES diagnostico(id_diagnostico) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 11. MANTENIMIENTO (posventa: preventivo / correctivo)  [RF-08]
-- ---------------------------------------------------------------------
CREATE TABLE mantenimiento (
    id_mantenimiento INT AUTO_INCREMENT PRIMARY KEY,
    id_instalacion   INT NOT NULL,
    id_empleado      INT NOT NULL,
    tipo             ENUM('Preventivo','Correctivo') NOT NULL,
    fecha            DATE NOT NULL,
    descripcion      TEXT,
    costo            DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    CONSTRAINT fk_mant_instalacion FOREIGN KEY (id_instalacion)
        REFERENCES instalacion(id_instalacion) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_mant_empleado FOREIGN KEY (id_empleado)
        REFERENCES empleado(id_empleado) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 12. GARANTIA (garantia de los equipos vendidos)  [RF-09]
-- ---------------------------------------------------------------------
CREATE TABLE garantia (
    id_garantia       INT AUTO_INCREMENT PRIMARY KEY,
    id_venta          INT NOT NULL,
    id_producto       INT NOT NULL,
    fecha_inicio      DATE NOT NULL,
    meses_garantia    INT NOT NULL,
    fecha_vencimiento DATE NOT NULL,
    estado            ENUM('Vigente','Vencida','Anulada') NOT NULL DEFAULT 'Vigente',
    condiciones       VARCHAR(200),
    CONSTRAINT fk_garantia_venta FOREIGN KEY (id_venta)
        REFERENCES venta(id_venta) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_garantia_producto FOREIGN KEY (id_producto)
        REFERENCES producto(id_producto) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 13. SOPORTE_TECNICO (solicitudes y atencion posventa)  [RF-10]
-- ---------------------------------------------------------------------
CREATE TABLE soporte_tecnico (
    id_soporte     INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente     INT NOT NULL,
    id_empleado    INT NOT NULL,
    id_instalacion INT,
    fecha          DATE NOT NULL,
    tipo           ENUM('Consulta','Incidencia','Reclamo') NOT NULL,
    descripcion    TEXT,
    estado         ENUM('Abierto','En proceso','Cerrado') NOT NULL DEFAULT 'Abierto',
    solucion       TEXT,
    CONSTRAINT fk_soporte_cliente FOREIGN KEY (id_cliente)
        REFERENCES cliente(id_cliente) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_soporte_empleado FOREIGN KEY (id_empleado)
        REFERENCES empleado(id_empleado) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_soporte_instalacion FOREIGN KEY (id_instalacion)
        REFERENCES instalacion(id_instalacion) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 14. ORDEN_COMPRA (compra a proveedor)
-- ---------------------------------------------------------------------
CREATE TABLE orden_compra (
    id_orden     INT AUTO_INCREMENT PRIMARY KEY,
    id_proveedor INT NOT NULL,
    id_empleado  INT NOT NULL,
    fecha        DATE NOT NULL,
    estado       ENUM('Emitida','Recibida','Anulada') NOT NULL DEFAULT 'Emitida',
    total        DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    CONSTRAINT fk_orden_proveedor FOREIGN KEY (id_proveedor)
        REFERENCES proveedor(id_proveedor) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_orden_empleado FOREIGN KEY (id_empleado)
        REFERENCES empleado(id_empleado) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 15. DETALLE_ORDEN_COMPRA (lineas - resuelve N:M)
-- ---------------------------------------------------------------------
CREATE TABLE detalle_orden_compra (
    id_detalle_orden INT AUTO_INCREMENT PRIMARY KEY,
    id_orden         INT NOT NULL,
    id_producto      INT NOT NULL,
    cantidad         INT NOT NULL,
    costo_unitario   DECIMAL(10,2) NOT NULL,
    CONSTRAINT uq_detalle_orden UNIQUE (id_orden, id_producto),
    CONSTRAINT fk_detorden_orden FOREIGN KEY (id_orden)
        REFERENCES orden_compra(id_orden) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_detorden_producto FOREIGN KEY (id_producto)
        REFERENCES producto(id_producto) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 16. MOVIMIENTO_INVENTARIO (Kardex)  [RF-04]
-- ---------------------------------------------------------------------
CREATE TABLE movimiento_inventario (
    id_movimiento    INT AUTO_INCREMENT PRIMARY KEY,
    id_producto      INT NOT NULL,
    tipo_movimiento  ENUM('Entrada','Salida') NOT NULL,
    cantidad         INT NOT NULL,
    fecha            DATE NOT NULL,
    referencia       VARCHAR(100),
    stock_resultante INT,
    CONSTRAINT fk_movinv_producto FOREIGN KEY (id_producto)
        REFERENCES producto(id_producto) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;
-- =====================================================================
--  ELECTRIC LIFE  ·  Script DML (Manipulacion de datos)
--  Insercion de datos de ejemplo  ·  Ejecutar DESPUES del DDL.
-- =====================================================================
USE electric_life;

-- EMPLEADOS (los tres socios)
INSERT INTO empleado (nombres, apellidos, cedula, rol, telefono, correo) VALUES
('Daniel Fernando','Allacuri Quilligana','1600123456','Supervisor Tecnico','0997327168','df_allacuriq@electriclife.com'),
('Jhoer Fernando','Fernandez Medina','1600234567','Tecnico Instalador','0987654321','jhoer.fernandez@electriclife.com'),
('Liz Sandra','Pena Veliz','1600345678','Compras y Logistica','0976543210','liz.pena@electriclife.com');

-- PROVEEDORES
INSERT INTO proveedor (nombre, ubicacion, telefono, correo, suministro_principal) VALUES
('Proviento','Nacional','022500000','ventas@proviento.com.ec','Paneles, inversores y baterias de gel y litio'),
('Pintulac','Cadena nacional','1800746852','info@pintulac.com.ec','Paneles solares, inversores y baterias'),
('Sunny Future','Quito','022600000','info@sunnyfuture.co','Baterias de litio (LiFePO4), inversores hibridos'),
('Amawtec','Quito / Imbabura','062600000','ventas@amawtec.com','Distribuidor oficial de kits Growatt'),
('Grupo RQ','Nacional','042700000','ventas@gruporq.ec','Soluciones con tecnologia Victron Energy'),
('Deltaglobal S.A.','Nacional','022800000','info@deltaglobal.com.ec','Equipos premium con garantias de hasta 25 anios');

-- CATEGORIAS DE PRODUCTO (con clasificacion ABC)
INSERT INTO categoria_producto (nombre_categoria, clasificacion_abc, descripcion) VALUES
('Panel Solar','A','Modulos fotovoltaicos monocristalinos/policristalinos'),
('Inversor','A','Inversores hibridos y off-grid'),
('Bateria','A','Bancos de almacenamiento de litio y gel'),
('Regulador','B','Controladores de carga MPPT/PWM'),
('Proteccion','B','Breakers, fusibles y protecciones DC/AC'),
('Cableado','C','Cables fotovoltaicos, terminales y conectores'),
('Estructura','C','Soportes y estructuras de montaje');

-- PRODUCTOS
INSERT INTO producto (id_categoria, id_proveedor, nombre_modelo, marca, precio_venta, garantia_meses) VALUES
(1, 4, 'Panel monocristalino 450W','Growatt', 180.00, 300),
(2, 4, 'Inversor hibrido 3kW','Growatt', 650.00, 120),
(3, 3, 'Bateria LiFePO4 100Ah 12V','SRNE', 520.00, 120),
(4, 5, 'Regulador de carga MPPT 60A','Victron', 140.00, 60),
(5, 2, 'Breaker DC 63A','Chint', 25.00, 12),
(6, 2, 'Cable fotovoltaico 6mm (metro)','General Cable', 2.50, 12),
(7, 1, 'Estructura de montaje aluminio','Proviento', 45.00, 24);

-- CLIENTES
INSERT INTO cliente (tipo_cliente, nombre_razon_social, ruc_cedula, telefono, correo, direccion, ciudad, fecha_registro) VALUES
('Negocio','Farmacia Su Salud','1690012345001','032885001','farmaciasusalud@gmail.com','Av. Alberto Zambrano y 9 de Octubre','Puyo','2026-07-05'),
('Negocio','Ferreteria El Constructor','1690023456001','032885002','ferreteriaelconstructor@gmail.com','Calle Ceslao Marin y Atahualpa','Puyo','2026-07-06'),
('Negocio','Restaurante El Jardin','1690034567001','032885003','eljardinpuyo@gmail.com','Av. Ceslao Marin y Bolivar','Puyo','2026-07-08'),
('Hogar','Juan Andres Perez','1600456789','0991112233','juanperez@gmail.com','Barrio Obrero, calle Los Angeles','Puyo','2026-07-09'),
('Negocio','Cyber Amazonia','1690045678001','032885004','cyberamazonia@gmail.com','Calle 27 de Febrero y Sucre','Puyo','2026-07-10');

-- DIAGNOSTICOS
INSERT INTO diagnostico (id_cliente, fecha, consumo_estimado_wh, horas_respaldo, cargas_criticas) VALUES
(1, '2026-07-07', 1800.00, 4.0, 'Refrigerador de vacunas, iluminacion LED, sistema POS, router'),
(3, '2026-07-09', 2500.00, 3.0, 'Refrigeracion de alimentos, iluminacion, POS, congelador');

-- COTIZACIONES
INSERT INTO cotizacion (id_cliente, id_empleado, fecha, estado, total) VALUES
(1, 1, '2026-07-10', 'Aprobada', 2730.00),
(3, 1, '2026-07-20', 'Pendiente', 2770.00),
(5, 1, '2026-07-22', 'Aprobada', 1530.00);

-- DETALLE DE COTIZACIONES
INSERT INTO detalle_cotizacion (id_cotizacion, id_producto, cantidad, precio_unitario) VALUES
(1, 1, 4, 180.00),(1, 2, 1, 650.00),(1, 3, 2, 520.00),(1, 4, 1, 140.00),(1, 7, 4, 45.00),
(2, 1, 6, 180.00),(2, 2, 1, 650.00),(2, 3, 2, 520.00),
(3, 1, 2, 180.00),(3, 2, 1, 650.00),(3, 3, 1, 520.00);

-- VENTAS (de las cotizaciones aprobadas 1 y 3)
INSERT INTO venta (id_cotizacion, id_empleado, fecha_venta, forma_pago, total, anticipo, saldo) VALUES
(1, 1, '2026-07-12', 'Transferencia', 2730.00, 1365.00, 1365.00),
(3, 1, '2026-07-23', 'Efectivo', 1530.00, 1530.00, 0.00);

-- INSTALACIONES (de las ventas)
INSERT INTO instalacion (id_venta, id_empleado, id_diagnostico, fecha_inicio, fecha_entrega, estado, direccion_instalacion) VALUES
(1, 2, 1, '2026-07-15', '2026-07-18', 'Entregado', 'Av. Alberto Zambrano y 9 de Octubre, Puyo'),
(2, 2, NULL, '2026-07-25', NULL, 'En instalacion', 'Calle 27 de Febrero y Sucre, Puyo');

-- MANTENIMIENTO
INSERT INTO mantenimiento (id_instalacion, id_empleado, tipo, fecha, descripcion, costo) VALUES
(1, 2, 'Preventivo', '2026-08-15', 'Limpieza de paneles, revision de conexiones y prueba de autonomia', 40.00);

-- GARANTIAS (equipos vendidos en la venta 1 y 2)
INSERT INTO garantia (id_venta, id_producto, fecha_inicio, meses_garantia, fecha_vencimiento, estado, condiciones) VALUES
(1, 1, '2026-07-18', 300, '2051-07-18', 'Vigente', 'Garantia de rendimiento del panel (25 anios)'),
(1, 2, '2026-07-18', 120, '2036-07-18', 'Vigente', 'Garantia del inversor (10 anios)'),
(1, 3, '2026-07-18', 120, '2036-07-18', 'Vigente', 'Garantia de la bateria (10 anios)'),
(2, 2, '2026-07-25', 120, '2036-07-25', 'Vigente', 'Garantia del inversor (10 anios)');

-- SOPORTE TECNICO
INSERT INTO soporte_tecnico (id_cliente, id_empleado, id_instalacion, fecha, tipo, descripcion, estado, solucion) VALUES
(1, 1, 1, '2026-08-20', 'Consulta', 'Consulta sobre autonomia del sistema en dias nublados', 'Cerrado', 'Se explico el funcionamiento y se ajusto la configuracion del inversor'),
(5, 2, 2, '2026-08-01', 'Incidencia', 'El inversor emite una alarma intermitente', 'En proceso', NULL);

-- ORDEN DE COMPRA (reposicion de stock a Amawtec)
INSERT INTO orden_compra (id_proveedor, id_empleado, fecha, estado, total) VALUES
(4, 3, '2026-07-12', 'Recibida', 2540.00);

INSERT INTO detalle_orden_compra (id_orden, id_producto, cantidad, costo_unitario) VALUES
(1, 1, 10, 150.00),
(1, 2, 2, 520.00);

-- MOVIMIENTOS DE INVENTARIO (Kardex)
INSERT INTO movimiento_inventario (id_producto, tipo_movimiento, cantidad, fecha, referencia, stock_resultante) VALUES
(1, 'Entrada', 10, '2026-07-13', 'Orden de compra #1', 10),
(2, 'Entrada',  2, '2026-07-13', 'Orden de compra #1',  2),
(1, 'Salida',   4, '2026-07-15', 'Instalacion #1 - Farmacia Su Salud', 6),
(2, 'Salida',   1, '2026-07-15', 'Instalacion #1 - Farmacia Su Salud', 1),
(1, 'Salida',   2, '2026-07-25', 'Instalacion #2 - Cyber Amazonia', 4),
(2, 'Salida',   1, '2026-07-25', 'Instalacion #2 - Cyber Amazonia', 0);
-- =====================================================================
--  ELECTRIC LIFE  ·  Objetos de la base de datos
--  Vistas, Procedimientos almacenados e Indices
--  Ejecutar DESPUES del DDL y el DML.
-- =====================================================================
USE electric_life;

-- =====================================================================
--  VISTAS
-- =====================================================================

-- V1. Stock actual por producto (calculado desde el Kardex)
CREATE OR REPLACE VIEW vista_stock_producto AS
SELECT  p.id_producto,
        p.nombre_modelo,
        cat.nombre_categoria,
        COALESCE(SUM(CASE WHEN m.tipo_movimiento = 'Entrada' THEN m.cantidad
                          WHEN m.tipo_movimiento = 'Salida'  THEN -m.cantidad
                          ELSE 0 END), 0) AS stock_actual
FROM producto p
JOIN categoria_producto cat ON cat.id_categoria = p.id_categoria
LEFT JOIN movimiento_inventario m ON m.id_producto = p.id_producto
GROUP BY p.id_producto, p.nombre_modelo, cat.nombre_categoria;

-- V2. Cotizaciones con cliente y vendedor
CREATE OR REPLACE VIEW vista_cotizaciones_cliente AS
SELECT  co.id_cotizacion,
        cl.nombre_razon_social AS cliente,
        CONCAT(e.nombres, ' ', e.apellidos) AS vendedor,
        co.fecha,
        co.estado,
        co.total
FROM cotizacion co
JOIN cliente  cl ON cl.id_cliente  = co.id_cliente
JOIN empleado e  ON e.id_empleado  = co.id_empleado;

-- V3. Instalaciones con cliente, tecnico y valor de la venta
CREATE OR REPLACE VIEW vista_instalaciones_detalle AS
SELECT  i.id_instalacion,
        cl.nombre_razon_social AS cliente,
        CONCAT(e.nombres, ' ', e.apellidos) AS tecnico,
        v.total AS valor_venta,
        i.estado,
        i.fecha_inicio,
        i.fecha_entrega
FROM instalacion i
JOIN venta      v  ON v.id_venta       = i.id_venta
JOIN cotizacion co ON co.id_cotizacion = v.id_cotizacion
JOIN cliente    cl ON cl.id_cliente    = co.id_cliente
JOIN empleado   e  ON e.id_empleado    = i.id_empleado;

-- V4. Garantias vigentes por cliente y producto
CREATE OR REPLACE VIEW vista_garantias_vigentes AS
SELECT  g.id_garantia,
        cl.nombre_razon_social AS cliente,
        p.nombre_modelo AS producto,
        g.fecha_inicio,
        g.fecha_vencimiento,
        g.estado
FROM garantia g
JOIN venta      v  ON v.id_venta       = g.id_venta
JOIN cotizacion co ON co.id_cotizacion = v.id_cotizacion
JOIN cliente    cl ON cl.id_cliente    = co.id_cliente
JOIN producto   p  ON p.id_producto    = g.id_producto
WHERE g.estado = 'Vigente';

-- =====================================================================
--  PROCEDIMIENTOS ALMACENADOS
-- =====================================================================
DELIMITER $$

-- P1. Recalcula el total de una cotizacion a partir de su detalle
DROP PROCEDURE IF EXISTS sp_actualizar_total_cotizacion $$
CREATE PROCEDURE sp_actualizar_total_cotizacion (IN p_id_cotizacion INT)
BEGIN
    UPDATE cotizacion
       SET total = (SELECT COALESCE(SUM(cantidad * precio_unitario), 0)
                    FROM detalle_cotizacion
                    WHERE id_cotizacion = p_id_cotizacion)
     WHERE id_cotizacion = p_id_cotizacion;
END $$

-- P2. Registra un movimiento de inventario y calcula el stock resultante
DROP PROCEDURE IF EXISTS sp_registrar_movimiento $$
CREATE PROCEDURE sp_registrar_movimiento (
    IN p_id_producto INT,
    IN p_tipo        VARCHAR(10),
    IN p_cantidad    INT,
    IN p_fecha       DATE,
    IN p_referencia  VARCHAR(100)
)
BEGIN
    DECLARE v_stock INT;
    SELECT COALESCE(SUM(CASE WHEN tipo_movimiento='Entrada' THEN cantidad
                             WHEN tipo_movimiento='Salida'  THEN -cantidad
                             ELSE 0 END), 0)
      INTO v_stock
      FROM movimiento_inventario
     WHERE id_producto = p_id_producto;

    IF p_tipo = 'Entrada' THEN
        SET v_stock = v_stock + p_cantidad;
    ELSE
        SET v_stock = v_stock - p_cantidad;
    END IF;

    INSERT INTO movimiento_inventario (id_producto, tipo_movimiento, cantidad, fecha, referencia, stock_resultante)
    VALUES (p_id_producto, p_tipo, p_cantidad, p_fecha, p_referencia, v_stock);
END $$

-- P3. Reporte de ventas dentro de un rango de fechas
DROP PROCEDURE IF EXISTS sp_reporte_ventas $$
CREATE PROCEDURE sp_reporte_ventas (IN p_desde DATE, IN p_hasta DATE)
BEGIN
    SELECT  v.id_venta,
            cl.nombre_razon_social AS cliente,
            v.fecha_venta,
            v.forma_pago,
            v.total
    FROM venta v
    JOIN cotizacion co ON co.id_cotizacion = v.id_cotizacion
    JOIN cliente    cl ON cl.id_cliente    = co.id_cliente
    WHERE v.fecha_venta BETWEEN p_desde AND p_hasta
    ORDER BY v.fecha_venta;
END $$

DELIMITER ;

-- =====================================================================
--  INDICES (adicionales a los indices automaticos de las llaves)
-- =====================================================================
CREATE INDEX idx_cliente_nombre     ON cliente(nombre_razon_social);
CREATE INDEX idx_producto_nombre    ON producto(nombre_modelo);
CREATE INDEX idx_cotizacion_fecha   ON cotizacion(fecha);
CREATE INDEX idx_venta_fecha        ON venta(fecha_venta);
CREATE INDEX idx_movimiento_fecha   ON movimiento_inventario(fecha);
CREATE INDEX idx_garantia_vencim    ON garantia(fecha_vencimiento);
