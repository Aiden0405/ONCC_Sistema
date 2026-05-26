-- ONCC - Esquema PostgreSQL limpio y alineado al sistema Flask actual.
-- Basado en la idea del ERD recibido, pero normalizado y con nombres consistentes.

BEGIN;

CREATE TABLE IF NOT EXISTS estado (
    id_estado SERIAL PRIMARY KEY,
    nombre_estado VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS municipio (
    id_municipio SERIAL PRIMARY KEY,
    id_estado INTEGER NOT NULL REFERENCES estado(id_estado) ON UPDATE CASCADE ON DELETE RESTRICT,
    nombre_municipio VARCHAR(120) NOT NULL,
    UNIQUE (id_estado, nombre_municipio)
);

CREATE TABLE IF NOT EXISTS parroquia (
    id_parroquia SERIAL PRIMARY KEY,
    id_municipio INTEGER NOT NULL REFERENCES municipio(id_municipio) ON UPDATE CASCADE ON DELETE RESTRICT,
    nombre_parroquia VARCHAR(120) NOT NULL,
    UNIQUE (id_municipio, nombre_parroquia)
);

CREATE TABLE IF NOT EXISTS comunidad (
    id_comunidad SERIAL PRIMARY KEY,
    id_parroquia INTEGER NOT NULL REFERENCES parroquia(id_parroquia) ON UPDATE CASCADE ON DELETE RESTRICT,
    nombre_comunidad VARCHAR(180) NOT NULL,
    vocero VARCHAR(120),
    telefono VARCHAR(40),
    familias INTEGER NOT NULL DEFAULT 0 CHECK (familias >= 0),
    fase VARCHAR(60) NOT NULL DEFAULT 'Diagnóstico / Acercamiento',
    fecha_proximo DATE,
    creado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE (id_parroquia, nombre_comunidad)
);

CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL UNIQUE,
    descripcion VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS permissions (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL UNIQUE,
    descripcion VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    rol VARCHAR(50) NOT NULL DEFAULT 'Técnico',
    estatus BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS user_roles (
    user_id INTEGER NOT NULL REFERENCES usuarios(id) ON UPDATE CASCADE ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON UPDATE CASCADE ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE IF NOT EXISTS role_permissions (
    role_id INTEGER NOT NULL REFERENCES roles(id) ON UPDATE CASCADE ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES permissions(id) ON UPDATE CASCADE ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE IF NOT EXISTS bitacora_transacciones (
    id SERIAL PRIMARY KEY,
    modulo VARCHAR(40) NOT NULL,
    registro_id INTEGER NOT NULL,
    accion VARCHAR(60) NOT NULL,
    estado_nuevo VARCHAR(20),
    usuario VARCHAR(120) NOT NULL,
    detalle VARCHAR(255),
    creado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS visitas_portal (
    id SERIAL PRIMARY KEY,
    mes VARCHAR(7) NOT NULL UNIQUE,
    creado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS niveles (
    id_nivel SERIAL PRIMARY KEY,
    nombre_nivel VARCHAR(80) NOT NULL UNIQUE,
    descripcion TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tecnicos_campo (
    id_tecnico SERIAL PRIMARY KEY,
    cedula VARCHAR(20) NOT NULL UNIQUE,
    nombres VARCHAR(120) NOT NULL,
    apellidos VARCHAR(120) NOT NULL,
    telefono VARCHAR(40),
    cargo VARCHAR(80),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS actividades (
    id SERIAL PRIMARY KEY,
    area VARCHAR(120) NOT NULL,
    actividad VARCHAR(180) NOT NULL,
    responsable VARCHAR(120) NOT NULL,
    fecha DATE NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Planificada',
    estado_geo VARCHAR(80) NOT NULL DEFAULT 'Lara',
    municipio VARCHAR(120) NOT NULL DEFAULT 'Sin municipio',
    parroquia VARCHAR(120),
    descripcion TEXT,
    poblacion INTEGER NOT NULL DEFAULT 0 CHECK (poblacion >= 0),
    acuerdos TEXT,
    minuta_archivo VARCHAR(255),
    fotos_archivos TEXT,
    creado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS actividad_tecnicos (
    id SERIAL PRIMARY KEY,
    id_actividad INTEGER NOT NULL REFERENCES actividades(id) ON UPDATE CASCADE ON DELETE CASCADE,
    id_tecnico INTEGER NOT NULL REFERENCES tecnicos_campo(id_tecnico) ON UPDATE CASCADE ON DELETE RESTRICT,
    rol_en_actividad VARCHAR(80),
    UNIQUE (id_actividad, id_tecnico)
);

CREATE TABLE IF NOT EXISTS formaciones (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    descripcion TEXT,
    fecha DATE NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'borrador',
    comunidad_id INTEGER REFERENCES comunidad(id_comunidad) ON UPDATE CASCADE ON DELETE SET NULL,
    actividad_id INTEGER REFERENCES actividades(id) ON UPDATE CASCADE ON DELETE SET NULL,
    facilitador VARCHAR(120),
    asistentes INTEGER NOT NULL DEFAULT 0 CHECK (asistentes >= 0),
    creado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sensibilizaciones (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    descripcion TEXT,
    fecha DATE NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'borrador',
    comunidad_id INTEGER REFERENCES comunidad(id_comunidad) ON UPDATE CASCADE ON DELETE SET NULL,
    actividad_id INTEGER REFERENCES actividades(id) ON UPDATE CASCADE ON DELETE SET NULL,
    vocero VARCHAR(120),
    alcance INTEGER NOT NULL DEFAULT 0 CHECK (alcance >= 0),
    creado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mapas_riesgo (
    id SERIAL PRIMARY KEY,
    id_comunidad INTEGER NOT NULL REFERENCES comunidad(id_comunidad) ON UPDATE CASCADE ON DELETE RESTRICT,
    nombre VARCHAR(150) NOT NULL,
    archivo VARCHAR(255),
    version VARCHAR(30) NOT NULL DEFAULT 'v1.0',
    estado VARCHAR(20) NOT NULL DEFAULT 'borrador',
    responsable VARCHAR(120) NOT NULL DEFAULT 'Equipo ONCC',
    creado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mapas_climaticos (
    id SERIAL PRIMARY KEY,
    id_parroquia INTEGER NOT NULL REFERENCES parroquia(id_parroquia) ON UPDATE CASCADE ON DELETE RESTRICT,
    tipo_de_mapa VARCHAR(40) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    archivo VARCHAR(255),
    estado VARCHAR(20) NOT NULL DEFAULT 'borrador',
    version VARCHAR(30) NOT NULL DEFAULT 'v1.0',
    responsable VARCHAR(120) NOT NULL DEFAULT 'Equipo ONCC',
    creado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS monitoreo_climatico (
    id SERIAL PRIMARY KEY,
    nombre_monitoreo VARCHAR(120) NOT NULL,
    fecha DATE NOT NULL,
    id_parroquia INTEGER REFERENCES parroquia(id_parroquia) ON UPDATE CASCADE ON DELETE SET NULL,
    temperatura NUMERIC(5,2),
    lluvia_mm NUMERIC(7,2),
    humedad NUMERIC(5,2),
    observacion TEXT,
    creado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS inventario_equipos (
    id SERIAL PRIMARY KEY,
    tipo_equipo VARCHAR(120) NOT NULL,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    ubicacion VARCHAR(150) NOT NULL,
    estado_operativo VARCHAR(60) NOT NULL DEFAULT 'Operativo',
    estado_flujo VARCHAR(20) NOT NULL DEFAULT 'borrador',
    ultimo_mantenimiento DATE,
    responsable VARCHAR(120) NOT NULL DEFAULT 'Sin asignar',
    creado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reportes_transaccionales (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    modulo_origen VARCHAR(50) NOT NULL,
    rango_desde DATE,
    rango_hasta DATE,
    formato VARCHAR(20) NOT NULL DEFAULT 'PDF',
    estado VARCHAR(20) NOT NULL DEFAULT 'borrador',
    responsable VARCHAR(120) NOT NULL DEFAULT 'Analista ONCC',
    creado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS publicaciones (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(40) NOT NULL DEFAULT 'boletin',
    titulo VARCHAR(180) NOT NULL,
    resumen TEXT,
    contenido TEXT,
    estado VARCHAR(20) NOT NULL DEFAULT 'borrador',
    publicado_en TIMESTAMP WITHOUT TIME ZONE,
    creado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS password_resets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES usuarios(id) ON UPDATE CASCADE ON DELETE CASCADE,
    token VARCHAR(128) NOT NULL UNIQUE,
    creado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    expiracion TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    usado BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_usuario_correo ON usuarios(correo);
CREATE INDEX IF NOT EXISTS idx_bitacora_modulo_registro ON bitacora_transacciones(modulo, registro_id);
CREATE INDEX IF NOT EXISTS idx_actividades_fecha ON actividades(fecha DESC);
CREATE INDEX IF NOT EXISTS idx_reportes_estado ON reportes_transaccionales(estado);
CREATE INDEX IF NOT EXISTS idx_mapas_riesgo_comunidad ON mapas_riesgo(id_comunidad);
CREATE INDEX IF NOT EXISTS idx_mapas_climaticos_parroquia ON mapas_climaticos(id_parroquia);
CREATE INDEX IF NOT EXISTS idx_password_resets_user_id ON password_resets(user_id);

COMMIT;