-- LEGACY MIRROR.
-- Este archivo se conserva solo como referencia histórica.
-- La fuente activa del esquema es database/sql.sql.
BEGIN;


CREATE TABLE IF NOT EXISTS public.actividad
(
    id_actividad serial NOT NULL,
    fecha_actividad date NOT NULL,
    tipo_actividad character varying(20)[] NOT NULL,
    id_comunidad serial NOT NULL,
    id_nivel serial NOT NULL,
    PRIMARY KEY (id_actividad),
    UNIQUE (id_actividad, tipo_actividad)
);

CREATE TABLE IF NOT EXISTS public.formacion
(
    id_formacion serial NOT NULL,
    nombre_formacion text COLLATE pg_catalog."default" NOT NULL,
    "id_actividad " serial NOT NULL,
    id_institucion serial NOT NULL,
    PRIMARY KEY (id_formacion),
    UNIQUE ("id_actividad ")
);

CREATE TABLE IF NOT EXISTS public."sensibilizacion "
(
    id_sensivilizacion serial NOT NULL,
    nombre_sensivilizacion text COLLATE pg_catalog."default" NOT NULL,
    id_actividad serial NOT NULL,
    PRIMARY KEY (id_sensivilizacion),
    UNIQUE (id_actividad)
);

CREATE TABLE IF NOT EXISTS public.usuario
(
    id_usuario serial NOT NULL,
    nombre_usuario character varying(30)[] NOT NULL,
    "clave usuario" character varying(255)[] NOT NULL,
    id_rol serial NOT NULL,
    PRIMARY KEY (id_usuario)
);

CREATE TABLE IF NOT EXISTS public.roles
(
    id_rol serial NOT NULL,
    nombre_rol character varying(20)[] NOT NULL,
    PRIMARY KEY (id_rol)
);

CREATE TABLE IF NOT EXISTS public.tecnicos
(
    id_tecnicos serial NOT NULL,
    cedula character varying(10)[] NOT NULL,
    nombres character(25) NOT NULL,
    apellidos character varying(25)[] NOT NULL,
    PRIMARY KEY (id_tecnicos)
);

CREATE TABLE IF NOT EXISTS public.modelos_equipo
(
    id_modelos_equipo serial NOT NULL,
    nombre_modelos_equipo character varying(50)[] NOT NULL,
    id_categoria serial NOT NULL,
    modelo character varying(100) NOT NULL,
    marca character varying(50) NOT NULL,
    PRIMARY KEY (id_modelos_equipo)
);

CREATE TABLE IF NOT EXISTS public.monitoreo
(
    id_monitoreo serial NOT NULL,
    nombre_monitoreo character varying(50)[] NOT NULL,
    id_actividad serial NOT NULL,
    PRIMARY KEY (id_monitoreo),
    UNIQUE (id_actividad)
);

CREATE TABLE IF NOT EXISTS public.mapa_climatico
(
    id_mapa_climatico serial NOT NULL,
    tipo_de_mapa character varying(20)[] NOT NULL,
    id_parroquia serial NOT NULL,
    PRIMARY KEY (id_mapa_climatico)
);

CREATE TABLE IF NOT EXISTS public.comunidad
(
    id_comunidad serial NOT NULL,
    nombre_comunidad character varying(20)[] NOT NULL,
    id_parroquia serial NOT NULL,
    PRIMARY KEY (id_comunidad)
);

CREATE TABLE IF NOT EXISTS public.actividad_tecnico
(
    id_actividad_tecnico serial NOT NULL,
    id_actividad serial NOT NULL,
    id_tecnico serial NOT NULL,
    PRIMARY KEY (id_actividad_tecnico)
);

CREATE TABLE IF NOT EXISTS public.nivel
(
    id_nivel serial NOT NULL,
    nombre_nivel character varying(20)[] NOT NULL,
    "descripción " text NOT NULL,
    PRIMARY KEY (id_nivel)
);

CREATE TABLE IF NOT EXISTS public.material
(
    id_material serial NOT NULL,
    id_nivel serial NOT NULL,
    url character varying(250) NOT NULL,
    PRIMARY KEY (id_material)
);

CREATE TABLE IF NOT EXISTS public.mapa_riesgo
(
    id_mapa_riesgo serial NOT NULL,
    id_comunidad serial NOT NULL,
    "id_sensibilizacion " serial NOT NULL,
    PRIMARY KEY (id_mapa_riesgo)
);

CREATE TABLE IF NOT EXISTS public.municipio
(
    id_municipio serial NOT NULL,
    nombre_municipio character varying(20)[] NOT NULL,
    id_estado serial NOT NULL,
    PRIMARY KEY (id_municipio)
);

CREATE TABLE IF NOT EXISTS public.parroquia
(
    id_parroquia serial NOT NULL,
    nombre_parroquia character varying(30)[] NOT NULL,
    id_municipio serial NOT NULL,
    PRIMARY KEY (id_parroquia)
);

CREATE TABLE IF NOT EXISTS public.estado
(
    id_estado serial NOT NULL,
    nombre_estado character varying(30)[] NOT NULL,
    PRIMARY KEY (id_estado)
);

CREATE TABLE IF NOT EXISTS public."ubicacion "
(
    id_ubicacion serial NOT NULL,
    nombre_ubicacion character varying(50) NOT NULL,
    id_parroquia serial NOT NULL,
    PRIMARY KEY (id_ubicacion)
);

CREATE TABLE IF NOT EXISTS public.modulos
(
    id_modulo serial NOT NULL,
    nombre_modulo character varying(20) NOT NULL,
    descripcion_modulo text NOT NULL,
    PRIMARY KEY (id_modulo)
);

CREATE TABLE IF NOT EXISTS public.permiso
(
    id_permiso serial NOT NULL,
    id_modulo serial NOT NULL,
    id_rol serial NOT NULL,
    PRIMARY KEY (id_permiso)
);

CREATE TABLE IF NOT EXISTS public.movimientos
(
    id_movimientos serial NOT NULL,
    id_equipo serial NOT NULL,
    id_inventario_ubicacion_llegada serial,
    id_inventario_ubicacion_salida serial,
    tipo_operacion character varying(20) NOT NULL,
    PRIMARY KEY (id_movimientos)
);

CREATE TABLE IF NOT EXISTS public.modelo
(
    id_modelo serial NOT NULL,
    nombre_modelo character varying(20)[] NOT NULL,
    descripcion_modelo text NOT NULL,
    PRIMARY KEY (id_modelo)
);

CREATE TABLE IF NOT EXISTS public.divulgacion
(
    id_divulgacion serial NOT NULL,
    nombre_divulgacion character varying(50) NOT NULL,
    descripcion_divulgacion text NOT NULL,
    permiso_divulgacion character varying(20) NOT NULL,
    id_actividad serial NOT NULL,
    PRIMARY KEY (id_divulgacion),
    UNIQUE (id_actividad)
);

CREATE TABLE IF NOT EXISTS public.publicacion
(
    id_publicacion serial NOT NULL,
    titulo_publicacion character varying(50) NOT NULL,
    membrete text NOT NULL,
    fecha_publicacion date NOT NULL,
    estado_publicacion character varying(20) NOT NULL,
    id_divulgacion serial NOT NULL,
    PRIMARY KEY (id_publicacion),
    UNIQUE (id_divulgacion)
);

CREATE TABLE IF NOT EXISTS public.pruebas
(
    id_pruebas serial NOT NULL,
    id_actividad serial NOT NULL,
    fecha_subida date NOT NULL,
    PRIMARY KEY (id_pruebas)
);

CREATE TABLE IF NOT EXISTS public.imagenes
(
    id_imagen bigserial NOT NULL,
    url_imagen text NOT NULL,
    nombre_imagen character varying(50) NOT NULL,
    fecha_imagen date NOT NULL,
    PRIMARY KEY (id_imagen)
);

CREATE TABLE IF NOT EXISTS public.intitucion
(
    id_institucion serial NOT NULL,
    id_comunidad serial NOT NULL,
    nombre_institucion character varying(50) NOT NULL,
    tipo_intitucion character varying(20) NOT NULL,
    direccion_exacta character varying(100) NOT NULL,
    numero_contacto character varying(25) NOT NULL,
    correo_electronico character varying(40) NOT NULL,
    PRIMARY KEY (id_institucion)
);

CREATE TABLE IF NOT EXISTS public.equipo
(
    id_equipo serial NOT NULL,
    id_modelos_equipos serial NOT NULL,
    numero_serie character varying(250) NOT NULL,
    codigo_interno character varying(50) NOT NULL,
    estado character varying(30) NOT NULL,
    fecha_ingreso date NOT NULL,
    opservaciones text,
    PRIMARY KEY (id_equipo)
);

CREATE TABLE IF NOT EXISTS public.ubicacion_equipo
(
    id_ubicacion_equipo serial NOT NULL,
    id_ubicacion serial NOT NULL,
    id_equipo serial NOT NULL,
    nombre_ubicacion character varying(50) NOT NULL,
    PRIMARY KEY (id_ubicacion_equipo)
);

CREATE TABLE IF NOT EXISTS public.equipo_monitoreo
(
    id_monitoreo_equipo serial NOT NULL,
    id_equipo serial NOT NULL,
    id_monitoreo serial NOT NULL,
    PRIMARY KEY (id_monitoreo_equipo)
);

CREATE TABLE IF NOT EXISTS public.imagenes_publicacion
(
    id_imagen serial NOT NULL,
    id_publicacion serial NOT NULL,
    id_imagenes_publicacion serial NOT NULL,
    PRIMARY KEY (id_imagenes_publicacion)
);

CREATE TABLE IF NOT EXISTS public.imagenes_pruebas
(
    id_imagen serial NOT NULL,
    id_pruebas bigserial NOT NULL,
    id_imagenes_pruebas serial NOT NULL,
    PRIMARY KEY (id_imagenes_pruebas)
);

ALTER TABLE IF EXISTS public.actividad
    ADD FOREIGN KEY (id_nivel)
    REFERENCES public.nivel (id_nivel) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.actividad
    ADD FOREIGN KEY (id_comunidad)
    REFERENCES public.comunidad (id_comunidad) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.formacion
    ADD FOREIGN KEY ("id_actividad ")
    REFERENCES public.actividad (id_actividad) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.formacion
    ADD FOREIGN KEY (id_institucion)
    REFERENCES public.intitucion (id_institucion) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public."sensibilizacion "
    ADD FOREIGN KEY (id_actividad)
    REFERENCES public.actividad (id_actividad) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.usuario
    ADD CONSTRAINT fk_id_roll FOREIGN KEY (id_rol)
    REFERENCES public.roles (id_rol) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE RESTRICT
    NOT VALID;


ALTER TABLE IF EXISTS public.modelos_equipo
    ADD FOREIGN KEY (id_categoria)
    REFERENCES public.modelo (id_modelo) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.monitoreo
    ADD FOREIGN KEY (id_actividad)
    REFERENCES public.actividad (id_actividad) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.mapa_climatico
    ADD FOREIGN KEY (id_parroquia)
    REFERENCES public.parroquia (id_parroquia) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.comunidad
    ADD FOREIGN KEY (id_parroquia)
    REFERENCES public.parroquia (id_parroquia) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.actividad_tecnico
    ADD FOREIGN KEY (id_actividad)
    REFERENCES public.actividad (id_actividad) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.actividad_tecnico
    ADD FOREIGN KEY (id_tecnico)
    REFERENCES public.tecnicos (id_tecnicos) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.material
    ADD FOREIGN KEY (id_nivel)
    REFERENCES public.nivel (id_nivel) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.mapa_riesgo
    ADD FOREIGN KEY (id_comunidad)
    REFERENCES public.comunidad (id_comunidad) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.mapa_riesgo
    ADD FOREIGN KEY ("id_sensibilizacion ")
    REFERENCES public."sensibilizacion " (id_sensivilizacion) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.municipio
    ADD FOREIGN KEY (id_estado)
    REFERENCES public.estado (id_estado) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.parroquia
    ADD FOREIGN KEY (id_municipio)
    REFERENCES public.municipio (id_municipio) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public."ubicacion "
    ADD FOREIGN KEY (id_parroquia)
    REFERENCES public.parroquia (id_parroquia) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.permiso
    ADD FOREIGN KEY (id_rol)
    REFERENCES public.roles (id_rol) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.permiso
    ADD FOREIGN KEY (id_modulo)
    REFERENCES public.modulos (id_modulo) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.movimientos
    ADD FOREIGN KEY (id_equipo)
    REFERENCES public.equipo (id_equipo) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.movimientos
    ADD FOREIGN KEY (id_inventario_ubicacion_llegada)
    REFERENCES public."ubicacion " (id_ubicacion) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.movimientos
    ADD FOREIGN KEY (id_inventario_ubicacion_salida)
    REFERENCES public.ubicacion_equipo (id_ubicacion_equipo) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.divulgacion
    ADD FOREIGN KEY (id_actividad)
    REFERENCES public.actividad (id_actividad) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.publicacion
    ADD FOREIGN KEY (id_divulgacion)
    REFERENCES public.divulgacion (id_divulgacion) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.pruebas
    ADD FOREIGN KEY (id_actividad)
    REFERENCES public.actividad (id_actividad) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.intitucion
    ADD FOREIGN KEY (id_comunidad)
    REFERENCES public.comunidad (id_comunidad) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.equipo
    ADD FOREIGN KEY (id_modelos_equipos)
    REFERENCES public.modelos_equipo (id_modelos_equipo) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.ubicacion_equipo
    ADD FOREIGN KEY (id_equipo)
    REFERENCES public.equipo (id_equipo) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.ubicacion_equipo
    ADD FOREIGN KEY (id_ubicacion)
    REFERENCES public."ubicacion " (id_ubicacion) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.equipo_monitoreo
    ADD FOREIGN KEY (id_equipo)
    REFERENCES public.equipo (id_equipo) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.equipo_monitoreo
    ADD FOREIGN KEY (id_monitoreo)
    REFERENCES public.monitoreo (id_monitoreo) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.imagenes_publicacion
    ADD FOREIGN KEY (id_imagen)
    REFERENCES public.imagenes (id_imagen) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.imagenes_publicacion
    ADD FOREIGN KEY (id_publicacion)
    REFERENCES public.publicacion (id_publicacion) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.imagenes_pruebas
    ADD FOREIGN KEY (id_imagen)
    REFERENCES public.imagenes (id_imagen) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.imagenes_pruebas
    ADD FOREIGN KEY (id_pruebas)
    REFERENCES public.pruebas (id_pruebas) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


-- Tablas de compatibilidad para el runtime actual del sistema.
-- El ERD principal se conserva arriba; estas tablas permiten que los módulos heredados sigan funcionando.

CREATE TABLE IF NOT EXISTS public.publicaciones
(
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

CREATE TABLE IF NOT EXISTS public.bitacora_transacciones
(
    id SERIAL PRIMARY KEY,
    modulo VARCHAR(40) NOT NULL,
    registro_id INTEGER NOT NULL,
    accion VARCHAR(60) NOT NULL,
    estado_nuevo VARCHAR(20),
    usuario VARCHAR(120) NOT NULL,
    detalle VARCHAR(255),
    creado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.visitas_portal
(
    id SERIAL PRIMARY KEY,
    mes VARCHAR(7) NOT NULL UNIQUE,
    creado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.password_resets
(
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES public.usuario(id_usuario) ON UPDATE CASCADE ON DELETE CASCADE,
    token VARCHAR(128) NOT NULL UNIQUE,
    creado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    expiracion TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    usado BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS public.reportes_transaccionales
(
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

CREATE TABLE IF NOT EXISTS public.inventario_equipos
(
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

CREATE TABLE IF NOT EXISTS public.mapas_registro
(
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    tipo_mapa VARCHAR(40) NOT NULL,
    archivo VARCHAR(255),
    estado VARCHAR(20) NOT NULL DEFAULT 'borrador',
    version VARCHAR(30) NOT NULL DEFAULT 'v1.0',
    cobertura VARCHAR(120) NOT NULL DEFAULT 'Regional',
    responsable VARCHAR(120) NOT NULL DEFAULT 'Equipo Geomatica',
    creado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

END;