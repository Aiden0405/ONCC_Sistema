-- ==============================================================================
-- Modelo Entidad-Relación Unificado y Optimizado
-- Autor: Gabriel Castañeda
-- Motor: PostgreSQL
-- Diseño: Optimizaciones de Integridad, Triggers, Índices y Particionamiento
-- ==============================================================================

BEGIN;

-- ==============================================================================
-- 1. FUNCIONES Y TRIGGERS (Automatización)
-- ==============================================================================
CREATE OR REPLACE FUNCTION actualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ==============================================================================
-- 2. TABLAS DEL SISTEMA Y GLOBALES (Sin dependencias)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.alembic_version (
    version_num character varying(32) NOT NULL,
    PRIMARY KEY (version_num)
);

CREATE TABLE IF NOT EXISTS public.visitas_portal (
    id serial NOT NULL,
    mes character varying(7) NOT NULL,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.roles (
    id_rol serial NOT NULL,
    nombre_rol character varying(80) NOT NULL UNIQUE,
    PRIMARY KEY (id_rol)
);

CREATE TABLE IF NOT EXISTS public.estado (
    id_estado serial NOT NULL,
    nombre_estado character varying(80) NOT NULL UNIQUE,
    PRIMARY KEY (id_estado)
);

CREATE TABLE IF NOT EXISTS public.tema (
    id_tema serial NOT NULL,
    nombre_tema character varying(100) NOT NULL,
    descripcion_tema text,
    PRIMARY KEY (id_tema)
);

CREATE TABLE IF NOT EXISTS public.tecnicos (
    id_tecnico serial NOT NULL,
    cedula character varying(15) NOT NULL UNIQUE,
    nombres character varying(60) NOT NULL,
    apellidos character varying(60) NOT NULL,
    PRIMARY KEY (id_tecnico)
);

CREATE TABLE IF NOT EXISTS public.categoria (
    id_categoria serial NOT NULL,
    nombre_categoria character varying(50) NOT NULL,
    descripcion_categoria text NOT NULL,
    PRIMARY KEY (id_categoria)
);

CREATE TABLE IF NOT EXISTS public.modulos (
    id_modulo serial NOT NULL,
    nombre_modulo character varying(80) NOT NULL UNIQUE,
    descripcion_modulo text NOT NULL,
    PRIMARY KEY (id_modulo)
);

CREATE TABLE IF NOT EXISTS public.imagenes (
    id_imagen bigserial NOT NULL,
    url_imagen text NOT NULL,
    nombre_imagen character varying(100) NOT NULL,
    fecha_imagen date NOT NULL,
    PRIMARY KEY (id_imagen)
);

-- ==============================================================================
-- 3. GEOGRAFÍA Y USUARIOS
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.municipio (
    id_municipio serial NOT NULL,
    id_estado integer NOT NULL,
    nombre_municipio character varying(120) NOT NULL,
    PRIMARY KEY (id_municipio),
    FOREIGN KEY (id_estado) REFERENCES public.estado (id_estado) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS public.parroquia (
    id_parroquia serial NOT NULL,
    id_municipio integer NOT NULL,
    nombre_parroquia character varying(120) NOT NULL,
    PRIMARY KEY (id_parroquia),
    FOREIGN KEY (id_municipio) REFERENCES public.municipio (id_municipio) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS public.comunidad (
    id_comunidad serial NOT NULL,
    id_parroquia integer NOT NULL,
    nombre_comunidad character varying(180) NOT NULL,
    PRIMARY KEY (id_comunidad),
    FOREIGN KEY (id_parroquia) REFERENCES public.parroquia (id_parroquia) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS public.ubicacion (
    id_ubicacion serial NOT NULL,
    id_parroquia integer NOT NULL,
    nombre_ubicacion character varying(100) NOT NULL,
    PRIMARY KEY (id_ubicacion),
    FOREIGN KEY (id_parroquia) REFERENCES public.parroquia (id_parroquia) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS public.usuario (
    id_usuario serial NOT NULL,
    nombre_usuario character varying(30) NOT NULL,
    clave_usuario character varying(255) NOT NULL,
    id_rol integer NOT NULL,
    correo character varying(100),
    estatus boolean DEFAULT true,
    PRIMARY KEY (id_usuario),
    FOREIGN KEY (id_rol) REFERENCES public.roles (id_rol) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS public.password_resets (
    id serial NOT NULL,
    user_id integer NOT NULL,
    token character varying(128) NOT NULL UNIQUE,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    expiracion timestamp without time zone NOT NULL,
    usado boolean DEFAULT false NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES public.usuario (id_usuario) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS public.permiso (
    id_permiso serial NOT NULL,
    id_modulo integer NOT NULL,
    id_rol integer NOT NULL,
    PRIMARY KEY (id_permiso),
    FOREIGN KEY (id_modulo) REFERENCES public.modulos (id_modulo) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (id_rol) REFERENCES public.roles (id_rol) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ==============================================================================
-- 4. MÓDULO EDUCATIVO Y ACTIVIDADES
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.institucion (
    id_institucion serial NOT NULL,
    id_comunidad integer NOT NULL,
    nombre_institucion character varying(100) NOT NULL,
    tipo_institucion character varying(50) NOT NULL,
    direccion_exacta character varying(250) NOT NULL,
    numero_contacto character varying(25) NOT NULL,
    correo_electronico character varying(100) NOT NULL,
    PRIMARY KEY (id_institucion),
    FOREIGN KEY (id_comunidad) REFERENCES public.comunidad (id_comunidad) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS public.nivel (
    id_nivel serial NOT NULL,
    nombre_nivel character varying(80) NOT NULL UNIQUE,
    descripcion text NOT NULL,
    PRIMARY KEY (id_nivel)
);

CREATE TABLE IF NOT EXISTS public.material (
    id_material serial NOT NULL,
    id_nivel integer NOT NULL,
    id_tema integer NOT NULL,
    url character varying(250) NOT NULL,
    PRIMARY KEY (id_material),
    FOREIGN KEY (id_nivel) REFERENCES public.nivel (id_nivel) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (id_tema) REFERENCES public.tema (id_tema) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS public.actividad (
    id_actividad serial NOT NULL,
    fecha_actividad date NOT NULL,
    tipo_actividad character varying(50) NOT NULL,
    id_comunidad integer NOT NULL,
    id_nivel integer NOT NULL,
    PRIMARY KEY (id_actividad),
    UNIQUE (fecha_actividad, tipo_actividad, id_comunidad),
    FOREIGN KEY (id_comunidad) REFERENCES public.comunidad (id_comunidad) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (id_nivel) REFERENCES public.nivel (id_nivel) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS public.actividad_tecnico (
    id_actividad_tecnico serial NOT NULL,
    id_actividad integer NOT NULL,
    id_tecnico integer NOT NULL,
    PRIMARY KEY (id_actividad_tecnico),
    FOREIGN KEY (id_actividad) REFERENCES public.actividad (id_actividad) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (id_tecnico) REFERENCES public.tecnicos (id_tecnico) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS public.formacion (
    id_formacion serial NOT NULL,
    id_actividad integer NOT NULL UNIQUE,
    id_institucion integer NOT NULL,
    nombre_formacion text NOT NULL,
    PRIMARY KEY (id_formacion),
    FOREIGN KEY (id_actividad) REFERENCES public.actividad (id_actividad) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (id_institucion) REFERENCES public.institucion (id_institucion) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS public.sensibilizacion (
    id_sensibilizacion serial NOT NULL,
    id_actividad integer NOT NULL UNIQUE,
    nombre_sensibilizacion text NOT NULL,
    PRIMARY KEY (id_sensibilizacion),
    FOREIGN KEY (id_actividad) REFERENCES public.actividad (id_actividad) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS public.monitoreo (
    id_monitoreo serial NOT NULL,
    id_actividad integer NOT NULL UNIQUE,
    nombre_monitoreo character varying(100) NOT NULL,
    PRIMARY KEY (id_monitoreo),
    FOREIGN KEY (id_actividad) REFERENCES public.actividad (id_actividad) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS public.pruebas (
    id_pruebas serial NOT NULL,
    id_actividad integer NOT NULL,
    fecha_subida date NOT NULL,
    PRIMARY KEY (id_pruebas),
    FOREIGN KEY (id_actividad) REFERENCES public.actividad (id_actividad) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS public.divulgacion (
    id_divulgacion serial NOT NULL,
    id_actividad integer NOT NULL UNIQUE,
    nombre_divulgacion character varying(100) NOT NULL,
    descripcion_divulgacion text NOT NULL,
    permiso_divulgacion character varying(50) NOT NULL,
    PRIMARY KEY (id_divulgacion),
    FOREIGN KEY (id_actividad) REFERENCES public.actividad (id_actividad) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS public.publicaciones (
    id_publicacion serial NOT NULL,
    id_divulgacion integer,
    id_usuario integer NOT NULL,
    tipo character varying(40) NOT NULL,
    titulo_publicacion character varying(180) NOT NULL,
    membrete text,
    resumen text,
    contenido text,
    estado_publicacion character varying(20) NOT NULL,
    fecha_publicacion date NOT NULL,
    publicado_en timestamp without time zone,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    actualizado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (id_publicacion),
    FOREIGN KEY (id_divulgacion) REFERENCES public.divulgacion (id_divulgacion) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (id_usuario) REFERENCES public.usuario (id_usuario) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- Asignación de Trigger a Publicaciones
CREATE TRIGGER trg_publicaciones_actualizado
BEFORE UPDATE ON public.publicaciones
FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

-- ==============================================================================
-- 5. MÓDULO DE INVENTARIO Y EQUIPOS
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.modelos_equipo (
    id_modelos_equipo serial NOT NULL,
    id_categoria integer NOT NULL,
    nombre_modelos_equipo character varying(100) NOT NULL,
    modelo character varying(100) NOT NULL,
    marca character varying(50) NOT NULL,
    PRIMARY KEY (id_modelos_equipo),
    FOREIGN KEY (id_categoria) REFERENCES public.categoria (id_categoria) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS public.equipo (
    id_equipo serial NOT NULL,
    id_modelos_equipos integer NOT NULL,
    codigo_interno character varying(50) NOT NULL UNIQUE,
    numero_serie character varying(250),
    estado character varying(30) NOT NULL,
    fecha_ingreso date NOT NULL,
    observaciones text,
    PRIMARY KEY (id_equipo),
    FOREIGN KEY (id_modelos_equipos) REFERENCES public.modelos_equipo (id_modelos_equipo) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS public.ubicacion_equipo (
    id_ubicacion_equipo serial NOT NULL,
    id_ubicacion integer NOT NULL,
    id_equipo integer NOT NULL,
    nombre_ubicacion character varying(100) NOT NULL,
    PRIMARY KEY (id_ubicacion_equipo),
    FOREIGN KEY (id_ubicacion) REFERENCES public.ubicacion (id_ubicacion) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (id_equipo) REFERENCES public.equipo (id_equipo) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS public.movimientos (
    id_movimientos serial NOT NULL,
    id_equipo integer NOT NULL,
    id_inventario_ubicacion_llegada integer,
    id_inventario_ubicacion_salida integer,
    tipo_operacion character varying(50) NOT NULL,
    PRIMARY KEY (id_movimientos),
    FOREIGN KEY (id_equipo) REFERENCES public.equipo (id_equipo) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (id_inventario_ubicacion_llegada) REFERENCES public.ubicacion (id_ubicacion) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (id_inventario_ubicacion_salida) REFERENCES public.ubicacion_equipo (id_ubicacion_equipo) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS public.equipo_monitoreo (
    id_monitoreo_equipo serial NOT NULL,
    id_equipo integer NOT NULL,
    id_monitoreo integer NOT NULL,
    PRIMARY KEY (id_monitoreo_equipo),
    FOREIGN KEY (id_equipo) REFERENCES public.equipo (id_equipo) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (id_monitoreo) REFERENCES public.monitoreo (id_monitoreo) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ==============================================================================
-- 6. MAPAS, CLIMA Y PARTICIONAMIENTO
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.mapa_climatico (
    id_mapa_climatico serial NOT NULL,
    id_municipio integer NOT NULL,
    tipo_de_mapa character varying(50) NOT NULL,
    url_mapa character varying(250) NOT NULL,
    fecha_creacion date NOT NULL,
    PRIMARY KEY (id_mapa_climatico),
    FOREIGN KEY (id_municipio) REFERENCES public.municipio (id_municipio) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS public.mapa_riesgo (
    id_mapa_riesgo serial NOT NULL,
    id_comunidad integer NOT NULL,
    id_sensibilizacion integer NOT NULL,
    PRIMARY KEY (id_mapa_riesgo),
    FOREIGN KEY (id_comunidad) REFERENCES public.comunidad (id_comunidad) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (id_sensibilizacion) REFERENCES public.sensibilizacion (id_sensibilizacion) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- Tabla PARTICIONADA de Registros Climáticos (La PK debe incluir la llave de partición)
CREATE TABLE IF NOT EXISTS public.registros_climaticos (
    id_registro bigserial NOT NULL,
    fecha_registro date NOT NULL,
    id_equipo integer NOT NULL,
    id_mapa_climatico integer,
    temperatura real NOT NULL,
    precipitaciones real NOT NULL,
    vientos real NOT NULL,
    humedad real NOT NULL,
    PRIMARY KEY (id_registro, fecha_registro),
    UNIQUE (fecha_registro, id_equipo),
    FOREIGN KEY (id_equipo) REFERENCES public.equipo (id_equipo) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (id_mapa_climatico) REFERENCES public.mapa_climatico (id_mapa_climatico) ON UPDATE CASCADE ON DELETE RESTRICT
) PARTITION BY RANGE (fecha_registro);

-- Particiones anuales predeterminadas para los Registros Climáticos
CREATE TABLE registros_climaticos_2026 PARTITION OF public.registros_climaticos FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
CREATE TABLE registros_climaticos_2027 PARTITION OF public.registros_climaticos FOR VALUES FROM ('2027-01-01') TO ('2028-01-01');

-- ==============================================================================
-- 7. TABLAS DE CRUCE PARA IMÁGENES
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.imagenes_publicacion (
    id_imagenes_publicacion serial NOT NULL,
    id_imagen bigint NOT NULL,
    id_publicacion integer NOT NULL,
    PRIMARY KEY (id_imagenes_publicacion),
    FOREIGN KEY (id_imagen) REFERENCES public.imagenes (id_imagen) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (id_publicacion) REFERENCES public.publicaciones (id_publicacion) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS public.imagenes_pruebas (
    id_imagenes_pruebas serial NOT NULL,
    id_imagen bigint NOT NULL,
    id_pruebas integer NOT NULL,
    PRIMARY KEY (id_imagenes_pruebas),
    FOREIGN KEY (id_imagen) REFERENCES public.imagenes (id_imagen) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (id_pruebas) REFERENCES public.pruebas (id_pruebas) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ==============================================================================
-- 8. BITÁCORAS Y REPORTES DEL SISTEMA (Particionados y con Triggers)
-- ==============================================================================

-- Tabla PARTICIONADA de Bitácoras
CREATE TABLE IF NOT EXISTS public.bitacora_transacciones (
    id serial NOT NULL,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    modulo character varying(40) NOT NULL,
    registro_id integer NOT NULL,
    accion character varying(60) NOT NULL,
    estado_nuevo character varying(20),
    usuario character varying(120) NOT NULL,
    detalle character varying(255),
    PRIMARY KEY (id, creado_en)
) PARTITION BY RANGE (creado_en);

-- Particiones anuales predeterminadas para la Bitácora
CREATE TABLE bitacora_2026 PARTITION OF public.bitacora_transacciones FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
CREATE TABLE bitacora_2027 PARTITION OF public.bitacora_transacciones FOR VALUES FROM ('2027-01-01') TO ('2028-01-01');

CREATE TABLE IF NOT EXISTS public.reportes_transaccionales (
    id serial NOT NULL,
    titulo character varying(150) NOT NULL,
    modulo_origen character varying(50) NOT NULL,
    rango_desde date,
    rango_hasta date,
    formato character varying(20) NOT NULL,
    estado character varying(20) NOT NULL,
    responsable character varying(120) NOT NULL,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    actualizado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (id)
);

-- Asignación de Trigger a Reportes
CREATE TRIGGER trg_reportes_actualizado
BEFORE UPDATE ON public.reportes_transaccionales
FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

-- ==============================================================================
-- 9. ÍNDICES MANUALES DE OPTIMIZACIÓN (B-Tree para Llaves Foráneas)
-- ==============================================================================
CREATE INDEX idx_municipio_estado ON public.municipio(id_estado);
CREATE INDEX idx_parroquia_municipio ON public.parroquia(id_municipio);
CREATE INDEX idx_comunidad_parroquia ON public.comunidad(id_parroquia);
CREATE INDEX idx_ubicacion_parroquia ON public.ubicacion(id_parroquia);
CREATE INDEX idx_usuario_rol ON public.usuario(id_rol);
CREATE INDEX idx_password_user ON public.password_resets(user_id);
CREATE INDEX idx_permiso_modulo ON public.permiso(id_modulo);
CREATE INDEX idx_permiso_rol ON public.permiso(id_rol);
CREATE INDEX idx_institucion_comunidad ON public.institucion(id_comunidad);
CREATE INDEX idx_material_nivel ON public.material(id_nivel);
CREATE INDEX idx_material_tema ON public.material(id_tema);
CREATE INDEX idx_actividad_comunidad ON public.actividad(id_comunidad);
CREATE INDEX idx_actividad_nivel ON public.actividad(id_nivel);
CREATE INDEX idx_act_tec_actividad ON public.actividad_tecnico(id_actividad);
CREATE INDEX idx_act_tec_tecnico ON public.actividad_tecnico(id_tecnico);
CREATE INDEX idx_formacion_institucion ON public.formacion(id_institucion);
CREATE INDEX idx_publicaciones_divulgacion ON public.publicaciones(id_divulgacion);
CREATE INDEX idx_publicaciones_usuario ON public.publicaciones(id_usuario);
CREATE INDEX idx_modelos_categoria ON public.modelos_equipo(id_categoria);
CREATE INDEX idx_equipo_modelo ON public.equipo(id_modelos_equipos);
CREATE INDEX idx_ubic_eq_ubicacion ON public.ubicacion_equipo(id_ubicacion);
CREATE INDEX idx_ubic_eq_equipo ON public.ubicacion_equipo(id_equipo);
CREATE INDEX idx_movimientos_equipo ON public.movimientos(id_equipo);
CREATE INDEX idx_movimientos_ubic_llegada ON public.movimientos(id_inventario_ubicacion_llegada);
CREATE INDEX idx_movimientos_ubic_salida ON public.movimientos(id_inventario_ubicacion_salida);
CREATE INDEX idx_eq_monitoreo_equipo ON public.equipo_monitoreo(id_equipo);
CREATE INDEX idx_eq_monitoreo_monitoreo ON public.equipo_monitoreo(id_monitoreo);
CREATE INDEX idx_mapacli_municipio ON public.mapa_climatico(id_municipio);
CREATE INDEX idx_maparies_comunidad ON public.mapa_riesgo(id_comunidad);
CREATE INDEX idx_maparies_sensib ON public.mapa_riesgo(id_sensibilizacion);
CREATE INDEX idx_regcli_equipo ON public.registros_climaticos(id_equipo);
CREATE INDEX idx_regcli_mapa ON public.registros_climaticos(id_mapa_climatico);
CREATE INDEX idx_img_pub_imagen ON public.imagenes_publicacion(id_imagen);
CREATE INDEX idx_img_pub_publicacion ON public.imagenes_publicacion(id_publicacion);
CREATE INDEX idx_img_pru_imagen ON public.imagenes_pruebas(id_imagen);
CREATE INDEX idx_img_pru_pruebas ON public.imagenes_pruebas(id_pruebas);

COMMIT;