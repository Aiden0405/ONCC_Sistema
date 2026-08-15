--
-- PostgreSQL database dump
--

\restrict KV8z7ZB8lSY9t9q7cevsvleW97fFcdhHPg6YWyL2rRLtChgc8MVkYaqt47f1yzU

-- Dumped from database version 17.10
-- Dumped by pg_dump version 17.10

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';


--
-- Name: actualizar_timestamp(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.actualizar_timestamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.actualizado_en = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.actualizar_timestamp() OWNER TO postgres;

--
-- Name: validar_previa_sensibilizacion(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.validar_previa_sensibilizacion() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_id_comunidad integer;
    v_existe_sensibilizacion boolean;
BEGIN
    -- 1. Obtener el id_comunidad de la actividad que se intenta registrar como mapa de riesgo
    SELECT id_comunidad INTO v_id_comunidad 
    FROM public.actividad 
    WHERE id_actividad = NEW.id_actividad;

    -- 2. Verificar si esa misma comunidad posee al menos una actividad de tipo SENSIBILIZACION
    SELECT EXISTS (
        SELECT 1 
        FROM public.actividad a
        JOIN public.sensibilizacion s ON a.id_actividad = s.id_actividad
        WHERE a.id_comunidad = v_id_comunidad
    ) INTO v_existe_sensibilizacion;

    -- 3. Si no existe una sensibilización previa para la comunidad, se cancela la operación
    IF NOT v_existe_sensibilizacion THEN
        RAISE EXCEPTION 'Restricción de ONCC: No se puede registrar el mapa de riesgo. La comunidad asociada debe contar con una actividad de sensibilización previa.';
    END IF;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.validar_previa_sensibilizacion() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: actividad; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.actividad (
    id_actividad integer NOT NULL,
    fecha_actividad date NOT NULL,
    tipo_actividad character varying(50) NOT NULL,
    id_comunidad integer NOT NULL,
    id_nivel integer,
    id_usuario integer,
    descripcion text,
    poblacion integer DEFAULT 0,
    acuerdos text,
    minuta_archivo character varying(255)
);


ALTER TABLE public.actividad OWNER TO postgres;

--
-- Name: actividad_id_actividad_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.actividad_id_actividad_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.actividad_id_actividad_seq OWNER TO postgres;

--
-- Name: actividad_id_actividad_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.actividad_id_actividad_seq OWNED BY public.actividad.id_actividad;


--
-- Name: actividad_tecnico; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.actividad_tecnico (
    id_actividad_tecnico integer NOT NULL,
    id_actividad integer NOT NULL,
    id_tecnico integer NOT NULL
);


ALTER TABLE public.actividad_tecnico OWNER TO postgres;

--
-- Name: actividad_tecnico_id_actividad_tecnico_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.actividad_tecnico_id_actividad_tecnico_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.actividad_tecnico_id_actividad_tecnico_seq OWNER TO postgres;

--
-- Name: actividad_tecnico_id_actividad_tecnico_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.actividad_tecnico_id_actividad_tecnico_seq OWNED BY public.actividad_tecnico.id_actividad_tecnico;


--
-- Name: actividades; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.actividades (
    id integer NOT NULL,
    area character varying(120) NOT NULL,
    actividad character varying(180) NOT NULL,
    responsable character varying(120) NOT NULL,
    fecha date NOT NULL,
    estado character varying(20) NOT NULL,
    estado_geo character varying(80) NOT NULL,
    municipio character varying(120) NOT NULL,
    parroquia character varying(120),
    descripcion text,
    poblacion integer NOT NULL,
    acuerdos text,
    minuta_archivo character varying(255),
    fotos_archivos text,
    creado_en timestamp without time zone NOT NULL,
    actualizado_en timestamp without time zone NOT NULL
);


ALTER TABLE public.actividades OWNER TO postgres;

--
-- Name: actividades_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.actividades_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.actividades_id_seq OWNER TO postgres;

--
-- Name: actividades_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.actividades_id_seq OWNED BY public.actividades.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: bitacora_transacciones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bitacora_transacciones (
    id integer NOT NULL,
    modulo character varying(40) NOT NULL,
    registro_id integer NOT NULL,
    accion character varying(60) NOT NULL,
    estado_nuevo character varying(20),
    usuario character varying(120) NOT NULL,
    detalle character varying(255),
    creado_en timestamp without time zone NOT NULL
);


ALTER TABLE public.bitacora_transacciones OWNER TO postgres;

--
-- Name: bitacora_transacciones_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bitacora_transacciones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.bitacora_transacciones_id_seq OWNER TO postgres;

--
-- Name: bitacora_transacciones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bitacora_transacciones_id_seq OWNED BY public.bitacora_transacciones.id;


--
-- Name: categoria; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.categoria (
    id_categoria integer NOT NULL,
    nombre_categoria character varying(50) NOT NULL,
    descripcion_categoria text NOT NULL
);


ALTER TABLE public.categoria OWNER TO postgres;

--
-- Name: categoria_id_categoria_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.categoria_id_categoria_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categoria_id_categoria_seq OWNER TO postgres;

--
-- Name: categoria_id_categoria_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.categoria_id_categoria_seq OWNED BY public.categoria.id_categoria;


--
-- Name: comunidad; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.comunidad (
    id_comunidad integer NOT NULL,
    id_parroquia integer NOT NULL,
    nombre_comunidad character varying(180) NOT NULL
);


ALTER TABLE public.comunidad OWNER TO postgres;

--
-- Name: comunidad_id_comunidad_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.comunidad_id_comunidad_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.comunidad_id_comunidad_seq OWNER TO postgres;

--
-- Name: comunidad_id_comunidad_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.comunidad_id_comunidad_seq OWNED BY public.comunidad.id_comunidad;


--
-- Name: divulgacion; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.divulgacion (
    id_divulgacion integer NOT NULL,
    id_actividad integer NOT NULL,
    nombre_divulgacion character varying(100) NOT NULL,
    descripcion_divulgacion text NOT NULL,
    permiso_divulgacion character varying(50) NOT NULL
);


ALTER TABLE public.divulgacion OWNER TO postgres;

--
-- Name: divulgacion_id_divulgacion_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.divulgacion_id_divulgacion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.divulgacion_id_divulgacion_seq OWNER TO postgres;

--
-- Name: divulgacion_id_divulgacion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.divulgacion_id_divulgacion_seq OWNED BY public.divulgacion.id_divulgacion;


--
-- Name: elemento_mapa_riesgo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.elemento_mapa_riesgo (
    id_elemento integer NOT NULL,
    id_mapa_riesgo integer NOT NULL,
    categoria character varying(50) NOT NULL,
    subcategoria character varying(100) NOT NULL,
    descripcion text,
    geometria public.geometry(Geometry,4326) NOT NULL
);


ALTER TABLE public.elemento_mapa_riesgo OWNER TO postgres;

--
-- Name: elemento_mapa_riesgo_id_elemento_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.elemento_mapa_riesgo_id_elemento_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.elemento_mapa_riesgo_id_elemento_seq OWNER TO postgres;

--
-- Name: elemento_mapa_riesgo_id_elemento_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.elemento_mapa_riesgo_id_elemento_seq OWNED BY public.elemento_mapa_riesgo.id_elemento;


--
-- Name: equipo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.equipo (
    id_equipo integer NOT NULL,
    id_modelos_equipos integer NOT NULL,
    id_ubicacion_actual integer,
    codigo_interno character varying(50) NOT NULL,
    numero_serie character varying(250),
    estado character varying(30) NOT NULL,
    fecha_ingreso date NOT NULL,
    observaciones text
);


ALTER TABLE public.equipo OWNER TO postgres;

--
-- Name: equipo_id_equipo_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.equipo_id_equipo_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.equipo_id_equipo_seq OWNER TO postgres;

--
-- Name: equipo_id_equipo_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.equipo_id_equipo_seq OWNED BY public.equipo.id_equipo;


--
-- Name: equipo_monitoreo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.equipo_monitoreo (
    id_monitoreo_equipo integer NOT NULL,
    id_equipo integer NOT NULL,
    id_monitoreo integer NOT NULL
);


ALTER TABLE public.equipo_monitoreo OWNER TO postgres;

--
-- Name: equipo_monitoreo_id_monitoreo_equipo_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.equipo_monitoreo_id_monitoreo_equipo_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.equipo_monitoreo_id_monitoreo_equipo_seq OWNER TO postgres;

--
-- Name: equipo_monitoreo_id_monitoreo_equipo_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.equipo_monitoreo_id_monitoreo_equipo_seq OWNED BY public.equipo_monitoreo.id_monitoreo_equipo;


--
-- Name: estado; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.estado (
    id_estado integer NOT NULL,
    nombre_estado character varying(80) NOT NULL
);


ALTER TABLE public.estado OWNER TO postgres;

--
-- Name: estado_id_estado_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.estado_id_estado_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.estado_id_estado_seq OWNER TO postgres;

--
-- Name: estado_id_estado_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.estado_id_estado_seq OWNED BY public.estado.id_estado;


--
-- Name: formacion; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.formacion (
    id_formacion integer NOT NULL,
    id_actividad integer NOT NULL,
    id_institucion integer NOT NULL,
    nombre_formacion text NOT NULL,
    tipo_actividad character varying(50) DEFAULT 'FORMACION'::character varying NOT NULL,
    id_nivel integer NOT NULL,
    CONSTRAINT chk_solo_formacion CHECK (((tipo_actividad)::text = 'FORMACION'::text))
);


ALTER TABLE public.formacion OWNER TO postgres;

--
-- Name: formacion_id_formacion_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.formacion_id_formacion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.formacion_id_formacion_seq OWNER TO postgres;

--
-- Name: formacion_id_formacion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.formacion_id_formacion_seq OWNED BY public.formacion.id_formacion;


--
-- Name: imagenes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.imagenes (
    id_imagen bigint NOT NULL,
    url_imagen text NOT NULL,
    nombre_imagen character varying(100) NOT NULL,
    fecha_imagen date NOT NULL
);


ALTER TABLE public.imagenes OWNER TO postgres;

--
-- Name: imagenes_actividad; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.imagenes_actividad (
    id_imagenes_actividad integer NOT NULL,
    id_imagen bigint NOT NULL,
    id_actividad integer NOT NULL
);


ALTER TABLE public.imagenes_actividad OWNER TO postgres;

--
-- Name: imagenes_actividad_id_imagenes_actividad_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.imagenes_actividad_id_imagenes_actividad_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.imagenes_actividad_id_imagenes_actividad_seq OWNER TO postgres;

--
-- Name: imagenes_actividad_id_imagenes_actividad_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.imagenes_actividad_id_imagenes_actividad_seq OWNED BY public.imagenes_actividad.id_imagenes_actividad;


--
-- Name: imagenes_id_imagen_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.imagenes_id_imagen_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.imagenes_id_imagen_seq OWNER TO postgres;

--
-- Name: imagenes_id_imagen_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.imagenes_id_imagen_seq OWNED BY public.imagenes.id_imagen;


--
-- Name: imagenes_publicacion; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.imagenes_publicacion (
    id_imagenes_publicacion integer NOT NULL,
    id_imagen bigint NOT NULL,
    id_publicacion integer NOT NULL
);


ALTER TABLE public.imagenes_publicacion OWNER TO postgres;

--
-- Name: imagenes_publicacion_id_imagenes_publicacion_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.imagenes_publicacion_id_imagenes_publicacion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.imagenes_publicacion_id_imagenes_publicacion_seq OWNER TO postgres;

--
-- Name: imagenes_publicacion_id_imagenes_publicacion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.imagenes_publicacion_id_imagenes_publicacion_seq OWNED BY public.imagenes_publicacion.id_imagenes_publicacion;


--
-- Name: institucion; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.institucion (
    id_institucion integer NOT NULL,
    id_comunidad integer NOT NULL,
    nombre_institucion character varying(100) NOT NULL,
    tipo_institucion character varying(50) NOT NULL,
    direccion_exacta character varying(250) NOT NULL,
    numero_contacto character varying(25) NOT NULL,
    correo_electronico character varying(100) NOT NULL
);


ALTER TABLE public.institucion OWNER TO postgres;

--
-- Name: institucion_id_institucion_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.institucion_id_institucion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.institucion_id_institucion_seq OWNER TO postgres;

--
-- Name: institucion_id_institucion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.institucion_id_institucion_seq OWNED BY public.institucion.id_institucion;


--
-- Name: inventario_equipos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.inventario_equipos (
    id integer NOT NULL,
    tipo_equipo character varying(120) NOT NULL,
    codigo character varying(50) NOT NULL,
    ubicacion character varying(150) NOT NULL,
    estado_operativo character varying(60) NOT NULL,
    estado_flujo character varying(20) NOT NULL,
    ultimo_mantenimiento date,
    responsable character varying(120) NOT NULL,
    creado_en timestamp without time zone NOT NULL,
    actualizado_en timestamp without time zone NOT NULL
);


ALTER TABLE public.inventario_equipos OWNER TO postgres;

--
-- Name: inventario_equipos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.inventario_equipos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.inventario_equipos_id_seq OWNER TO postgres;

--
-- Name: inventario_equipos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.inventario_equipos_id_seq OWNED BY public.inventario_equipos.id;


--
-- Name: mapa_climatico; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mapa_climatico (
    id_mapa_climatico integer NOT NULL,
    id_municipio integer NOT NULL,
    tipo_de_mapa character varying(50) NOT NULL,
    url_mapa character varying(250) NOT NULL,
    fecha_creacion date NOT NULL
);


ALTER TABLE public.mapa_climatico OWNER TO postgres;

--
-- Name: mapa_climatico_id_mapa_climatico_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mapa_climatico_id_mapa_climatico_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mapa_climatico_id_mapa_climatico_seq OWNER TO postgres;

--
-- Name: mapa_climatico_id_mapa_climatico_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mapa_climatico_id_mapa_climatico_seq OWNED BY public.mapa_climatico.id_mapa_climatico;


--
-- Name: mapa_riesgo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mapa_riesgo (
    id_mapa_riesgo integer NOT NULL,
    id_actividad integer NOT NULL,
    tipo_actividad character varying(50) DEFAULT 'MAPA_RIESGO'::character varying NOT NULL,
    ruta_kml character varying(250),
    ruta_imagen_mapa character varying(250),
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    nombre character varying(100),
    descripcion text,
    CONSTRAINT chk_solo_mapa_riesgo CHECK (((tipo_actividad)::text = 'MAPA_RIESGO'::text))
);


ALTER TABLE public.mapa_riesgo OWNER TO postgres;

--
-- Name: mapa_riesgo_id_mapa_riesgo_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mapa_riesgo_id_mapa_riesgo_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mapa_riesgo_id_mapa_riesgo_seq OWNER TO postgres;

--
-- Name: mapa_riesgo_id_mapa_riesgo_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mapa_riesgo_id_mapa_riesgo_seq OWNED BY public.mapa_riesgo.id_mapa_riesgo;


--
-- Name: mapas_registro; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mapas_registro (
    id integer NOT NULL,
    nombre character varying(150) NOT NULL,
    tipo_mapa character varying(40) NOT NULL,
    archivo character varying(255),
    estado character varying(20) NOT NULL,
    version character varying(30) NOT NULL,
    cobertura character varying(120) NOT NULL,
    responsable character varying(120) NOT NULL,
    creado_en timestamp without time zone NOT NULL,
    actualizado_en timestamp without time zone NOT NULL
);


ALTER TABLE public.mapas_registro OWNER TO postgres;

--
-- Name: mapas_registro_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mapas_registro_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mapas_registro_id_seq OWNER TO postgres;

--
-- Name: mapas_registro_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mapas_registro_id_seq OWNED BY public.mapas_registro.id;


--
-- Name: material; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.material (
    id_material integer NOT NULL,
    id_nivel integer NOT NULL,
    id_tema integer NOT NULL,
    url character varying(250) NOT NULL
);


ALTER TABLE public.material OWNER TO postgres;

--
-- Name: material_id_material_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.material_id_material_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.material_id_material_seq OWNER TO postgres;

--
-- Name: material_id_material_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.material_id_material_seq OWNED BY public.material.id_material;


--
-- Name: modelos_equipo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.modelos_equipo (
    id_modelos_equipo integer NOT NULL,
    id_categoria integer NOT NULL,
    nombre_modelos_equipo character varying(100) NOT NULL,
    modelo character varying(100) NOT NULL,
    marca character varying(50) NOT NULL
);


ALTER TABLE public.modelos_equipo OWNER TO postgres;

--
-- Name: modelos_equipo_id_modelos_equipo_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.modelos_equipo_id_modelos_equipo_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.modelos_equipo_id_modelos_equipo_seq OWNER TO postgres;

--
-- Name: modelos_equipo_id_modelos_equipo_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.modelos_equipo_id_modelos_equipo_seq OWNED BY public.modelos_equipo.id_modelos_equipo;


--
-- Name: modulos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.modulos (
    id_modulo integer NOT NULL,
    nombre_modulo character varying(80) NOT NULL,
    descripcion_modulo text NOT NULL
);


ALTER TABLE public.modulos OWNER TO postgres;

--
-- Name: modulos_id_modulo_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.modulos_id_modulo_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.modulos_id_modulo_seq OWNER TO postgres;

--
-- Name: modulos_id_modulo_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.modulos_id_modulo_seq OWNED BY public.modulos.id_modulo;


--
-- Name: monitoreo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.monitoreo (
    id_monitoreo integer NOT NULL,
    id_actividad integer NOT NULL,
    nombre_monitoreo character varying(100) NOT NULL,
    tipo_actividad character varying(50) DEFAULT 'MONITOREO'::character varying NOT NULL,
    CONSTRAINT chk_solo_monitoreo CHECK (((tipo_actividad)::text = 'MONITOREO'::text))
);


ALTER TABLE public.monitoreo OWNER TO postgres;

--
-- Name: monitoreo_id_monitoreo_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.monitoreo_id_monitoreo_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.monitoreo_id_monitoreo_seq OWNER TO postgres;

--
-- Name: monitoreo_id_monitoreo_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.monitoreo_id_monitoreo_seq OWNED BY public.monitoreo.id_monitoreo;


--
-- Name: movimientos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.movimientos (
    id_movimientos integer NOT NULL,
    id_equipo integer NOT NULL,
    id_ubicacion_origen integer,
    id_ubicacion_destino integer NOT NULL,
    tipo_operacion character varying(50) NOT NULL,
    fecha_movimiento timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.movimientos OWNER TO postgres;

--
-- Name: movimientos_id_movimientos_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.movimientos_id_movimientos_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.movimientos_id_movimientos_seq OWNER TO postgres;

--
-- Name: movimientos_id_movimientos_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.movimientos_id_movimientos_seq OWNED BY public.movimientos.id_movimientos;


--
-- Name: municipio; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.municipio (
    id_municipio integer NOT NULL,
    id_estado integer NOT NULL,
    nombre_municipio character varying(120) NOT NULL
);


ALTER TABLE public.municipio OWNER TO postgres;

--
-- Name: municipio_id_municipio_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.municipio_id_municipio_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.municipio_id_municipio_seq OWNER TO postgres;

--
-- Name: municipio_id_municipio_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.municipio_id_municipio_seq OWNED BY public.municipio.id_municipio;


--
-- Name: nivel; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.nivel (
    id_nivel integer NOT NULL,
    nombre_nivel character varying(80) NOT NULL,
    descripcion text NOT NULL
);


ALTER TABLE public.nivel OWNER TO postgres;

--
-- Name: nivel_id_nivel_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.nivel_id_nivel_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.nivel_id_nivel_seq OWNER TO postgres;

--
-- Name: nivel_id_nivel_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.nivel_id_nivel_seq OWNED BY public.nivel.id_nivel;


--
-- Name: notificaciones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notificaciones (
    id integer NOT NULL,
    usuario_id integer,
    categoria character varying(50) DEFAULT 'Sistema'::character varying NOT NULL,
    mensaje text NOT NULL,
    leido boolean DEFAULT false,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.notificaciones OWNER TO postgres;

--
-- Name: notificaciones_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notificaciones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.notificaciones_id_seq OWNER TO postgres;

--
-- Name: notificaciones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notificaciones_id_seq OWNED BY public.notificaciones.id;


--
-- Name: parroquia; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.parroquia (
    id_parroquia integer NOT NULL,
    id_municipio integer NOT NULL,
    nombre_parroquia character varying(120) NOT NULL
);


ALTER TABLE public.parroquia OWNER TO postgres;

--
-- Name: parroquia_id_parroquia_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.parroquia_id_parroquia_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.parroquia_id_parroquia_seq OWNER TO postgres;

--
-- Name: parroquia_id_parroquia_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.parroquia_id_parroquia_seq OWNED BY public.parroquia.id_parroquia;


--
-- Name: password_resets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.password_resets (
    id integer NOT NULL,
    user_id integer NOT NULL,
    token character varying(128) NOT NULL,
    creado_en timestamp without time zone NOT NULL,
    expiracion timestamp without time zone NOT NULL,
    usado boolean NOT NULL
);


ALTER TABLE public.password_resets OWNER TO postgres;

--
-- Name: password_resets_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.password_resets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.password_resets_id_seq OWNER TO postgres;

--
-- Name: password_resets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.password_resets_id_seq OWNED BY public.password_resets.id;


--
-- Name: permiso; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.permiso (
    id_modulo integer,
    id_rol integer
);


ALTER TABLE public.permiso OWNER TO postgres;

--
-- Name: publicaciones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.publicaciones (
    id_publicacion integer NOT NULL,
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
    prioridad integer DEFAULT 1
);


ALTER TABLE public.publicaciones OWNER TO postgres;

--
-- Name: publicaciones_id_publicacion_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.publicaciones_id_publicacion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.publicaciones_id_publicacion_seq OWNER TO postgres;

--
-- Name: publicaciones_id_publicacion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.publicaciones_id_publicacion_seq OWNED BY public.publicaciones.id_publicacion;


--
-- Name: registros_climaticos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.registros_climaticos (
    id_registro bigint NOT NULL,
    fecha_registro date NOT NULL,
    id_equipo integer NOT NULL,
    id_mapa_climatico integer,
    temperatura real NOT NULL,
    precipitaciones real NOT NULL,
    vientos real NOT NULL,
    humedad real NOT NULL
);


ALTER TABLE public.registros_climaticos OWNER TO postgres;

--
-- Name: registros_climaticos_id_registro_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.registros_climaticos_id_registro_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.registros_climaticos_id_registro_seq OWNER TO postgres;

--
-- Name: registros_climaticos_id_registro_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.registros_climaticos_id_registro_seq OWNED BY public.registros_climaticos.id_registro;


--
-- Name: reportes_transaccionales; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reportes_transaccionales (
    id integer NOT NULL,
    titulo character varying(150) NOT NULL,
    modulo_origen character varying(50) NOT NULL,
    rango_desde date,
    rango_hasta date,
    formato character varying(20) NOT NULL,
    estado character varying(20) NOT NULL,
    responsable character varying(120) NOT NULL,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    actualizado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.reportes_transaccionales OWNER TO postgres;

--
-- Name: reportes_transaccionales_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reportes_transaccionales_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reportes_transaccionales_id_seq OWNER TO postgres;

--
-- Name: reportes_transaccionales_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reportes_transaccionales_id_seq OWNED BY public.reportes_transaccionales.id;


--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id_rol integer NOT NULL,
    nombre_rol character varying(80) NOT NULL
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: roles_id_rol_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_id_rol_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_id_rol_seq OWNER TO postgres;

--
-- Name: roles_id_rol_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_id_rol_seq OWNED BY public.roles.id_rol;


--
-- Name: sensibilizacion; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sensibilizacion (
    id_sensibilizacion integer NOT NULL,
    id_actividad integer NOT NULL,
    nombre_sensibilizacion text NOT NULL,
    tipo_actividad character varying(50) DEFAULT 'SENSIBILIZACION'::character varying NOT NULL,
    id_nivel integer NOT NULL,
    CONSTRAINT chk_solo_sensibilizacion CHECK (((tipo_actividad)::text = 'SENSIBILIZACION'::text))
);


ALTER TABLE public.sensibilizacion OWNER TO postgres;

--
-- Name: sensibilizacion_id_sensibilizacion_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sensibilizacion_id_sensibilizacion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sensibilizacion_id_sensibilizacion_seq OWNER TO postgres;

--
-- Name: sensibilizacion_id_sensibilizacion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sensibilizacion_id_sensibilizacion_seq OWNED BY public.sensibilizacion.id_sensibilizacion;


--
-- Name: tecnicos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tecnicos (
    id_tecnico integer NOT NULL,
    cedula character varying(15) NOT NULL,
    nombres character varying(60) NOT NULL,
    apellidos character varying(60) NOT NULL
);


ALTER TABLE public.tecnicos OWNER TO postgres;

--
-- Name: tecnicos_id_tecnico_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tecnicos_id_tecnico_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tecnicos_id_tecnico_seq OWNER TO postgres;

--
-- Name: tecnicos_id_tecnico_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tecnicos_id_tecnico_seq OWNED BY public.tecnicos.id_tecnico;


--
-- Name: tema; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tema (
    id_tema integer NOT NULL,
    nombre_tema character varying(100) NOT NULL,
    descripcion_tema text
);


ALTER TABLE public.tema OWNER TO postgres;

--
-- Name: tema_id_tema_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tema_id_tema_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tema_id_tema_seq OWNER TO postgres;

--
-- Name: tema_id_tema_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tema_id_tema_seq OWNED BY public.tema.id_tema;


--
-- Name: ubicacion; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ubicacion (
    id_ubicacion integer NOT NULL,
    id_parroquia integer NOT NULL,
    nombre_ubicacion character varying(100) NOT NULL
);


ALTER TABLE public.ubicacion OWNER TO postgres;

--
-- Name: ubicacion_id_ubicacion_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ubicacion_id_ubicacion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ubicacion_id_ubicacion_seq OWNER TO postgres;

--
-- Name: ubicacion_id_ubicacion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ubicacion_id_ubicacion_seq OWNED BY public.ubicacion.id_ubicacion;


--
-- Name: usuario; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuario (
    id_usuario integer NOT NULL,
    nombre_usuario character varying(30) NOT NULL,
    "clave usuario" character varying(255) NOT NULL,
    id_rol integer NOT NULL,
    correo character varying(100),
    cedula character varying(15),
    especialidad character varying(120),
    estatus boolean
);


ALTER TABLE public.usuario OWNER TO postgres;

--
-- Name: usuario_id_usuario_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.usuario_id_usuario_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usuario_id_usuario_seq OWNER TO postgres;

--
-- Name: usuario_id_usuario_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.usuario_id_usuario_seq OWNED BY public.usuario.id_usuario;


--
-- Name: visitas_portal; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.visitas_portal (
    id integer NOT NULL,
    mes character varying(7) NOT NULL,
    creado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.visitas_portal OWNER TO postgres;

--
-- Name: visitas_portal_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.visitas_portal_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.visitas_portal_id_seq OWNER TO postgres;

--
-- Name: visitas_portal_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.visitas_portal_id_seq OWNED BY public.visitas_portal.id;


--
-- Name: actividad id_actividad; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.actividad ALTER COLUMN id_actividad SET DEFAULT nextval('public.actividad_id_actividad_seq'::regclass);


--
-- Name: actividad_tecnico id_actividad_tecnico; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.actividad_tecnico ALTER COLUMN id_actividad_tecnico SET DEFAULT nextval('public.actividad_tecnico_id_actividad_tecnico_seq'::regclass);


--
-- Name: actividades id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.actividades ALTER COLUMN id SET DEFAULT nextval('public.actividades_id_seq'::regclass);


--
-- Name: bitacora_transacciones id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bitacora_transacciones ALTER COLUMN id SET DEFAULT nextval('public.bitacora_transacciones_id_seq'::regclass);


--
-- Name: categoria id_categoria; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categoria ALTER COLUMN id_categoria SET DEFAULT nextval('public.categoria_id_categoria_seq'::regclass);


--
-- Name: comunidad id_comunidad; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comunidad ALTER COLUMN id_comunidad SET DEFAULT nextval('public.comunidad_id_comunidad_seq'::regclass);


--
-- Name: divulgacion id_divulgacion; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.divulgacion ALTER COLUMN id_divulgacion SET DEFAULT nextval('public.divulgacion_id_divulgacion_seq'::regclass);


--
-- Name: elemento_mapa_riesgo id_elemento; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.elemento_mapa_riesgo ALTER COLUMN id_elemento SET DEFAULT nextval('public.elemento_mapa_riesgo_id_elemento_seq'::regclass);


--
-- Name: equipo id_equipo; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipo ALTER COLUMN id_equipo SET DEFAULT nextval('public.equipo_id_equipo_seq'::regclass);


--
-- Name: equipo_monitoreo id_monitoreo_equipo; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipo_monitoreo ALTER COLUMN id_monitoreo_equipo SET DEFAULT nextval('public.equipo_monitoreo_id_monitoreo_equipo_seq'::regclass);


--
-- Name: estado id_estado; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estado ALTER COLUMN id_estado SET DEFAULT nextval('public.estado_id_estado_seq'::regclass);


--
-- Name: formacion id_formacion; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.formacion ALTER COLUMN id_formacion SET DEFAULT nextval('public.formacion_id_formacion_seq'::regclass);


--
-- Name: imagenes id_imagen; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.imagenes ALTER COLUMN id_imagen SET DEFAULT nextval('public.imagenes_id_imagen_seq'::regclass);


--
-- Name: imagenes_actividad id_imagenes_actividad; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.imagenes_actividad ALTER COLUMN id_imagenes_actividad SET DEFAULT nextval('public.imagenes_actividad_id_imagenes_actividad_seq'::regclass);


--
-- Name: imagenes_publicacion id_imagenes_publicacion; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.imagenes_publicacion ALTER COLUMN id_imagenes_publicacion SET DEFAULT nextval('public.imagenes_publicacion_id_imagenes_publicacion_seq'::regclass);


--
-- Name: institucion id_institucion; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.institucion ALTER COLUMN id_institucion SET DEFAULT nextval('public.institucion_id_institucion_seq'::regclass);


--
-- Name: inventario_equipos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventario_equipos ALTER COLUMN id SET DEFAULT nextval('public.inventario_equipos_id_seq'::regclass);


--
-- Name: mapa_climatico id_mapa_climatico; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mapa_climatico ALTER COLUMN id_mapa_climatico SET DEFAULT nextval('public.mapa_climatico_id_mapa_climatico_seq'::regclass);


--
-- Name: mapa_riesgo id_mapa_riesgo; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mapa_riesgo ALTER COLUMN id_mapa_riesgo SET DEFAULT nextval('public.mapa_riesgo_id_mapa_riesgo_seq'::regclass);


--
-- Name: mapas_registro id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mapas_registro ALTER COLUMN id SET DEFAULT nextval('public.mapas_registro_id_seq'::regclass);


--
-- Name: material id_material; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.material ALTER COLUMN id_material SET DEFAULT nextval('public.material_id_material_seq'::regclass);


--
-- Name: modelos_equipo id_modelos_equipo; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modelos_equipo ALTER COLUMN id_modelos_equipo SET DEFAULT nextval('public.modelos_equipo_id_modelos_equipo_seq'::regclass);


--
-- Name: modulos id_modulo; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modulos ALTER COLUMN id_modulo SET DEFAULT nextval('public.modulos_id_modulo_seq'::regclass);


--
-- Name: monitoreo id_monitoreo; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.monitoreo ALTER COLUMN id_monitoreo SET DEFAULT nextval('public.monitoreo_id_monitoreo_seq'::regclass);


--
-- Name: movimientos id_movimientos; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movimientos ALTER COLUMN id_movimientos SET DEFAULT nextval('public.movimientos_id_movimientos_seq'::regclass);


--
-- Name: municipio id_municipio; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.municipio ALTER COLUMN id_municipio SET DEFAULT nextval('public.municipio_id_municipio_seq'::regclass);


--
-- Name: nivel id_nivel; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nivel ALTER COLUMN id_nivel SET DEFAULT nextval('public.nivel_id_nivel_seq'::regclass);


--
-- Name: notificaciones id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notificaciones ALTER COLUMN id SET DEFAULT nextval('public.notificaciones_id_seq'::regclass);


--
-- Name: parroquia id_parroquia; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parroquia ALTER COLUMN id_parroquia SET DEFAULT nextval('public.parroquia_id_parroquia_seq'::regclass);


--
-- Name: password_resets id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_resets ALTER COLUMN id SET DEFAULT nextval('public.password_resets_id_seq'::regclass);


--
-- Name: publicaciones id_publicacion; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.publicaciones ALTER COLUMN id_publicacion SET DEFAULT nextval('public.publicaciones_id_publicacion_seq'::regclass);


--
-- Name: registros_climaticos id_registro; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registros_climaticos ALTER COLUMN id_registro SET DEFAULT nextval('public.registros_climaticos_id_registro_seq'::regclass);


--
-- Name: reportes_transaccionales id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reportes_transaccionales ALTER COLUMN id SET DEFAULT nextval('public.reportes_transaccionales_id_seq'::regclass);


--
-- Name: roles id_rol; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id_rol SET DEFAULT nextval('public.roles_id_rol_seq'::regclass);


--
-- Name: sensibilizacion id_sensibilizacion; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sensibilizacion ALTER COLUMN id_sensibilizacion SET DEFAULT nextval('public.sensibilizacion_id_sensibilizacion_seq'::regclass);


--
-- Name: tecnicos id_tecnico; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tecnicos ALTER COLUMN id_tecnico SET DEFAULT nextval('public.tecnicos_id_tecnico_seq'::regclass);


--
-- Name: tema id_tema; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tema ALTER COLUMN id_tema SET DEFAULT nextval('public.tema_id_tema_seq'::regclass);


--
-- Name: ubicacion id_ubicacion; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ubicacion ALTER COLUMN id_ubicacion SET DEFAULT nextval('public.ubicacion_id_ubicacion_seq'::regclass);


--
-- Name: usuario id_usuario; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario ALTER COLUMN id_usuario SET DEFAULT nextval('public.usuario_id_usuario_seq'::regclass);


--
-- Name: visitas_portal id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.visitas_portal ALTER COLUMN id SET DEFAULT nextval('public.visitas_portal_id_seq'::regclass);


--
-- Data for Name: actividad; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.actividad (id_actividad, fecha_actividad, tipo_actividad, id_comunidad, id_nivel, id_usuario, descripcion, poblacion, acuerdos, minuta_archivo) FROM stdin;
15	2026-08-15	MONITOREO	1	1	4	Modo ejemplo	12	Compromiso comunitario.	uploads/minutas/WhatsApp_Image_2026-03-30_at_5.38.37_PM.pdf
16	2026-08-14	FORMACION	11	1	4	\N	0	\N	\N
17	2026-08-14	SENSIBILIZACION	1	1	4	\N	0	\N	\N
\.


--
-- Data for Name: actividad_tecnico; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.actividad_tecnico (id_actividad_tecnico, id_actividad, id_tecnico) FROM stdin;
17	15	2
\.


--
-- Data for Name: actividades; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.actividades (id, area, actividad, responsable, fecha, estado, estado_geo, municipio, parroquia, descripcion, poblacion, acuerdos, minuta_archivo, fotos_archivos, creado_en, actualizado_en) FROM stdin;
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
7653e1663a01
\.


--
-- Data for Name: bitacora_transacciones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bitacora_transacciones (id, modulo, registro_id, accion, estado_nuevo, usuario, detalle, creado_en) FROM stdin;
1	Usuarios	17	Eliminar	\N	Aileen Moyeja	Eliminado usuario pytest_auth_1783573339@oncc.gob.ve	2026-07-09 20:10:17.281072
2	Usuarios	16	Eliminar	\N	Aileen Moyeja	Eliminado usuario pytest_auth_1783572065@oncc.gob.ve	2026-07-09 20:10:23.239532
3	Usuarios	15	Eliminar	\N	Aileen Moyeja	Eliminado usuario pytest_auth_1783536797@oncc.gob.ve	2026-07-10 12:50:17.361982
4	Usuarios	14	Eliminar	\N	Aileen Moyeja	Eliminado usuario pytest_auth_1783551159@oncc.gob.ve	2026-07-10 12:50:21.718605
5	Roles	3	Modificar	\N	Aileen Moyeja	Actualizado rol Tecnico	2026-07-10 21:16:41.336911
6	Roles	2	Modificar	\N	Aileen Moyeja	Actualizado rol Administrador	2026-07-10 21:17:12.521653
7	Roles	2	ActualizarPermisos	\N	Aileen Moyeja	Permisos actualizados para Administrador: []	2026-07-10 21:17:32.266669
8	Roles	3	ActualizarPermisos	\N	Aileen Moyeja	Permisos actualizados para Tecnico: ['3', '2', '1']	2026-07-10 21:19:29.673485
9	Roles	6	Crear	\N	Aileen Moyeja	Creado rol secretaria	2026-07-10 21:21:45.84747
10	Roles	3	ActualizarPermisos	\N	Aileen Moyeja	Permisos actualizados para Tecnico: []	2026-07-10 21:25:36.626154
11	Roles	7	Crear	\N	Aileen Moyeja	Creado rol test	2026-07-11 16:25:47.117091
12	Roles	7	ActualizarPermisos	\N	Aileen Moyeja	Permisos actualizados para test: ['3']	2026-07-11 16:26:12.114484
13	Roles	7	Modificar	\N	Aileen Moyeja	Actualizado rol Divulgador	2026-07-11 16:26:32.626705
14	Roles	7	ActualizarPermisos	\N	Aileen Moyeja	Permisos actualizados para Divulgador: ['3', '2']	2026-07-11 16:26:49.551408
15	Roles	6	Modificar	\N	Aileen Moyeja	Actualizado rol Secretaria	2026-07-13 15:44:27.676466
16	Permisos	4	Crear	\N	Aileen Moyeja	Creado el privilegio atómico: ver_formaciones	2026-07-13 21:33:31.799996
17	Permisos	4	Modificar	\N	Aileen Moyeja	Actualizado el privilegio técnico a: ver_formaciones	2026-07-13 21:34:54.358126
18	Permisos	4	Eliminar	\N	Aileen Moyeja	Eliminado el privilegio atómico: ver_formaciones	2026-07-13 21:34:59.027845
19	Permisos	4	Crear	\N	Aileen Moyeja	Creado el privilegio atómico: ver_formaciones	2026-07-13 21:36:47.843572
20	Usuarios	18	Crear	Tecnico	Aileen Moyeja	Creado usuario luis@gmail.com	2026-07-13 23:14:36.959622
21	Usuarios	18	Eliminar	\N	Aileen Moyeja	Eliminado usuario luis@gmail.com	2026-07-13 23:15:02.387037
22	Usuarios	19	Crear	Tecnico	Aileen Moyeja	Creado usuario nirkules@fosil.pro	2026-07-13 23:15:22.470101
23	Usuarios	20	Crear	Secretaria	Aileen Moyeja	Creado usuario roman@gmail.com	2026-07-14 02:23:37.837528
24	Usuarios	20	Modificar	Secretaria	Genghis Khan	Editado usuario roman@gmail.com	2026-07-14 02:32:28.604685
25	Usuarios	20	Modificar	Secretaria	Aileen Moyeja	Editado usuario roman@gmail.com	2026-07-14 02:35:01.991268
26	Usuarios	20	Eliminar	\N	Aileen Moyeja	Eliminado usuario roman@gmail.com	2026-07-14 02:35:45.208876
27	Usuarios	21	Crear	Divulgador	Aileen Moyeja	Creado usuario andres@gmail.com	2026-07-14 03:04:18.024489
28	Roles	6	Modificar	\N	Aileen Moyeja	Actualizado rol Secretarias	2026-07-14 08:56:31.530629
29	Roles	6	Modificar	\N	Aileen Moyeja	Actualizado rol Secretaria	2026-07-14 09:00:00.137141
30	Usuarios	19	Modificar	Tecnico	Aileen Moyeja	Editado usuario nirkules@fosil.pro	2026-07-14 09:10:13.560826
31	Roles	8	Crear	\N	Aileen Moyeja	Creado rol Analista	2026-07-14 09:11:46.781069
32	Roles	8	Modificar	\N	Aileen Moyeja	Actualizado rol Analistas	2026-07-14 09:20:07.597016
33	Roles	8	Modificar	\N	Aileen Moyeja	Actualizado rol Analista	2026-07-14 09:22:56.872875
34	Roles	8	ActualizarPermisos	\N	Aileen Moyeja	Permisos actualizados para Analista: ['2']	2026-07-14 09:23:06.815171
35	Permisos	4	Modificar	\N	Aileen Moyeja	Actualizado el privilegio técnico a: ver_formaciones	2026-07-14 09:23:46.401613
36	Usuarios	11	Eliminar	\N	Aileen Moyeja	Eliminado usuario perez@gmail.com	2026-07-14 09:24:16.081031
37	Usuarios	22	Crear	Analista	Aileen Moyeja	Creado usuario angelo@gmail.com	2026-07-14 09:29:09.719831
38	Permisos	2	Modificar	\N	Aileen Moyeja	Actualizado el privilegio técnico a: crear_divulgaciones	2026-07-14 21:45:52.638262
39	Permisos	3	Modificar	\N	Genghis Khan	Actualizado el privilegio técnico a: aprobar_divulgaciones	2026-07-14 21:46:59.399046
40	Permisos	5	Crear	\N	Aileen Moyeja	Creado el privilegio atómico: gestionar_formaciones	2026-07-15 08:28:34.34559
41	Permisos	6	Crear	\N	Aileen Moyeja	Creado el privilegio atómico: gestionar_sensibilizaciones	2026-07-15 08:29:01.196206
42	Permisos	7	Crear	\N	Aileen Moyeja	Creado el privilegio atómico: registro_zenka	2026-07-15 08:31:02.238767
43	Permisos	7	Eliminar	\N	Aileen Moyeja	Eliminado el privilegio atómico: registro_zenka	2026-07-15 08:31:09.565008
44	Permisos	6	Eliminar	\N	Aileen Moyeja	Eliminado el privilegio atómico: gestionar_sensibilizaciones	2026-07-15 08:35:42.828684
45	Permisos	5	Eliminar	\N	Aileen Moyeja	Eliminado el privilegio atómico: gestionar_formaciones	2026-07-15 08:35:47.483427
46	Permisos	4	Eliminar	\N	Aileen Moyeja	Eliminado el privilegio atómico: ver_formaciones	2026-07-15 08:37:20.235862
47	Permisos	4	Crear	\N	Aileen Moyeja	Creado el privilegio atómico: gestionar_inventario	2026-07-15 08:44:43.786472
48	Permisos	4	Eliminar	\N	Aileen Moyeja	Eliminado el privilegio atómico: gestionar_inventario	2026-07-15 08:51:27.887866
49	Permisos	4	Crear	\N	Aileen Moyeja	Creado el privilegio atómico: gestionar_formaciones	2026-07-15 08:51:44.218961
50	Permisos	5	Crear	\N	Aileen Moyeja	Creado el privilegio atómico: gestionar_sensibilizaciones	2026-07-15 08:52:09.424817
51	Permisos	6	Crear	\N	Aileen Moyeja	Creado el privilegio atómico: gestionar_geomatica	2026-07-15 08:53:43.97628
52	Permisos	7	Crear	\N	Aileen Moyeja	Creado el privilegio atómico: ver_mapas	2026-07-15 08:54:08.333126
53	Permisos	8	Crear	\N	Aileen Moyeja	Creado el privilegio atómico: gestionar_inventario	2026-07-15 08:54:52.856838
54	Permisos	9	Crear	\N	Aileen Moyeja	Creado el privilegio atómico: gestionar_tecnicos	2026-07-15 08:57:59.176223
55	Roles	3	ActualizarPermisos	\N	Aileen Moyeja	Permisos actualizados para Tecnico: ['4', '8', '9', '7']	2026-07-15 08:58:50.589765
56	Roles	3	ActualizarPermisos	\N	Aileen Moyeja	Permisos actualizados para Tecnico: []	2026-07-15 08:59:06.153428
57	Roles	3	ActualizarPermisos	\N	Aileen Moyeja	Permisos actualizados para Tecnico: ['4', '5']	2026-07-15 09:03:07.289669
58	Roles	3	ActualizarPermisos	\N	Aileen Moyeja	Permisos actualizados para Tecnico: ['3', '2', '4', '6', '8', '5', '9', '1', '7']	2026-07-15 09:08:27.464345
59	Roles	3	ActualizarPermisos	\N	Aileen Moyeja	Permisos actualizados para Tecnico: ['4', '5']	2026-07-15 09:14:42.086581
60	Roles	3	ActualizarPermisos	\N	Aileen Moyeja	Permisos actualizados para Tecnico: ['4', '5']	2026-07-15 09:17:13.141527
61	Roles	3	ActualizarPermisos	\N	Aileen Moyeja	Permisos actualizados para Tecnico: ['3', '2', '4', '6', '8', '5', '9', '1', '7']	2026-07-15 09:19:55.103563
62	Roles	8	ActualizarPermisos	\N	Aileen Moyeja	Permisos actualizados para Analista: ['2']	2026-07-15 09:20:20.113991
63	Permisos	10	Crear	\N	Aileen Moyeja	Creado el privilegio atómico: gestionar_actividades	2026-07-15 09:23:29.040349
64	Roles	3	ActualizarPermisos	\N	Aileen Moyeja	Permisos actualizados para Tecnico: []	2026-07-15 09:25:38.584089
65	Roles	3	ActualizarPermisos	\N	Aileen Moyeja	Permisos actualizados para Tecnico: ['6']	2026-07-15 09:29:17.416401
66	actividades	4	creacion	Planificada	Aileen Moyeja	Actividad Sensibilización Comunitaria registrada	2026-08-12 23:11:37.236247
67	actividades	4	cambio_estado	Completado	Aileen Moyeja	Actividad Sensibilización Comunitaria paso a Completado	2026-08-12 23:13:46.289859
68	actividades	6	creacion	Completado	Aileen Moyeja	Actividad Taller de sensibilizacion comunitaria. registrada	2026-08-13 10:49:50.917581
69	actividades	6	edicion	Planificada	Aileen Moyeja	Actividad Taller de sensibilizacion comunitaria. modificada	2026-08-13 10:56:59.096466
70	actividades	6	edicion	\N	Aileen Moyeja	Actividad Taller de sensibilizacion comunitaria. modificada	2026-08-13 21:37:01.263673
71	actividades	6	edicion	Completado	Aileen Moyeja	Actividad Taller de sensibilizacion comunitaria. actualizada	2026-08-13 22:49:19.310118
72	actividades	6	edicion	Completado	Aileen Moyeja	Actividad Taller de sensibilizacion comunitaria. actualizada	2026-08-13 23:02:45.812003
73	actividades	6	edicion	Completado	Aileen Moyeja	Actividad Taller de sensibilizacion comunitaria. actualizada	2026-08-13 23:03:42.413294
74	actividades	6	edicion	Completado	Aileen Moyeja	Actividad Taller de sensibilizacion comunitaria. actualizada	2026-08-13 23:16:16.333617
75	actividades	6	edicion	En proceso	Aileen Moyeja	Actividad Taller de sensibilizacion comunitaria. actualizada	2026-08-13 23:16:48.379562
76	actividades	6	edicion	En proceso	Aileen Moyeja	Actividad MONITOREO actualizada a En proceso	2026-08-13 23:24:17.80572
77	actividades	6	edicion	Completado	Aileen Moyeja	Actividad MONITOREO actualizada a Completado	2026-08-13 23:24:36.188503
78	actividades	6	edicion	Completado	Aileen Moyeja	Actividad MONITOREO actualizada a Completado	2026-08-13 23:26:18.916
79	actividades	15	creacion	Suspendida	Aileen Moyeja	Actividad SENSIBILIZACION registrada en Suspendida	2026-08-13 23:52:00.904013
80	actividades	15	edicion	Completado	Aileen Moyeja	Actividad MONITOREO actualizada a Completado	2026-08-14 11:41:24.481166
81	Divulgación	4	Crear	borrador	Aileen Moyeja	Creado contenido: Titulo de articulo...	2026-08-14 11:53:14.604412
82	Divulgación	4	Modificar	publicado	Aileen Moyeja	Aprobada para la Web: Titulo de articulo...	2026-08-14 11:53:42.111932
\.


--
-- Data for Name: categoria; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.categoria (id_categoria, nombre_categoria, descripcion_categoria) FROM stdin;
\.


--
-- Data for Name: comunidad; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.comunidad (id_comunidad, id_parroquia, nombre_comunidad) FROM stdin;
1	1	Comunidad Central
11	1	Comunidad Oriental
\.


--
-- Data for Name: divulgacion; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.divulgacion (id_divulgacion, id_actividad, nombre_divulgacion, descripcion_divulgacion, permiso_divulgacion) FROM stdin;
1	15	Jornada Informativa	Describa el propósito.	Público
\.


--
-- Data for Name: elemento_mapa_riesgo; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.elemento_mapa_riesgo (id_elemento, id_mapa_riesgo, categoria, subcategoria, descripcion, geometria) FROM stdin;
\.


--
-- Data for Name: equipo; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.equipo (id_equipo, id_modelos_equipos, id_ubicacion_actual, codigo_interno, numero_serie, estado, fecha_ingreso, observaciones) FROM stdin;
\.


--
-- Data for Name: equipo_monitoreo; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.equipo_monitoreo (id_monitoreo_equipo, id_equipo, id_monitoreo) FROM stdin;
\.


--
-- Data for Name: estado; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.estado (id_estado, nombre_estado) FROM stdin;
1	Lara
\.


--
-- Data for Name: formacion; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.formacion (id_formacion, id_actividad, id_institucion, nombre_formacion, tipo_actividad, id_nivel) FROM stdin;
4	16	2	Gestion de Riesgo||Alcides Romero	FORMACION	1
\.


--
-- Data for Name: imagenes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.imagenes (id_imagen, url_imagen, nombre_imagen, fecha_imagen) FROM stdin;
1	uploads/fotos_actividad/ee0dc581fdff27eaace9110ae2d62367.jpg	ee0dc581fdff27eaace9110ae2d62367.jpg	2026-08-13
7	uploads/fotos_actividad/ee0dc581fdff27eaace9110ae2d62367.jpg	ee0dc581fdff27eaace9110ae2d62367.jpg	2026-08-13
\.


--
-- Data for Name: imagenes_actividad; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.imagenes_actividad (id_imagenes_actividad, id_imagen, id_actividad) FROM stdin;
2	7	15
\.


--
-- Data for Name: imagenes_publicacion; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.imagenes_publicacion (id_imagenes_publicacion, id_imagen, id_publicacion) FROM stdin;
\.


--
-- Data for Name: institucion; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.institucion (id_institucion, id_comunidad, nombre_institucion, tipo_institucion, direccion_exacta, numero_contacto, correo_electronico) FROM stdin;
1	1	UPTAEB	Educativa	Sede Comunitaria	S/N	contacto@oncc.gob.ve
2	1	IUJO	Educativa	Sede Comunitaria	S/N	contacto@oncc.gob.ve
\.


--
-- Data for Name: inventario_equipos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.inventario_equipos (id, tipo_equipo, codigo, ubicacion, estado_operativo, estado_flujo, ultimo_mantenimiento, responsable, creado_en, actualizado_en) FROM stdin;
\.


--
-- Data for Name: mapa_climatico; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mapa_climatico (id_mapa_climatico, id_municipio, tipo_de_mapa, url_mapa, fecha_creacion) FROM stdin;
\.


--
-- Data for Name: mapa_riesgo; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mapa_riesgo (id_mapa_riesgo, id_actividad, tipo_actividad, ruta_kml, ruta_imagen_mapa, fecha_registro, nombre, descripcion) FROM stdin;
\.


--
-- Data for Name: mapas_registro; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mapas_registro (id, nombre, tipo_mapa, archivo, estado, version, cobertura, responsable, creado_en, actualizado_en) FROM stdin;
\.


--
-- Data for Name: material; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.material (id_material, id_nivel, id_tema, url) FROM stdin;
\.


--
-- Data for Name: modelos_equipo; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.modelos_equipo (id_modelos_equipo, id_categoria, nombre_modelos_equipo, modelo, marca) FROM stdin;
\.


--
-- Data for Name: modulos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.modulos (id_modulo, nombre_modulo, descripcion_modulo) FROM stdin;
\.


--
-- Data for Name: monitoreo; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.monitoreo (id_monitoreo, id_actividad, nombre_monitoreo, tipo_actividad) FROM stdin;
7	15	Taller de Sensibilización comunitaria	MONITOREO
\.


--
-- Data for Name: movimientos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.movimientos (id_movimientos, id_equipo, id_ubicacion_origen, id_ubicacion_destino, tipo_operacion, fecha_movimiento) FROM stdin;
\.


--
-- Data for Name: municipio; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.municipio (id_municipio, id_estado, nombre_municipio) FROM stdin;
1	1	Iribarren
\.


--
-- Data for Name: nivel; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.nivel (id_nivel, nombre_nivel, descripcion) FROM stdin;
1	Regional	Nivel de cobertura regional para la actividad
3	Local	Nivel formativo e institucional: Local
4	Comunal	Ámbito Comunal
\.


--
-- Data for Name: notificaciones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notificaciones (id, usuario_id, categoria, mensaje, leido, fecha_creacion) FROM stdin;
7	\N	Seguridad	Estructura RBAC: Rol institucional 'Analista' renombrado a 'Analistas' por Aileen Moyeja.	t	2026-07-14 09:20:07.576725
8	\N	Seguridad	Estructura RBAC: Rol institucional 'Analistas' renombrado a 'Analista' por Aileen Moyeja.	t	2026-07-14 09:22:56.85689
9	\N	Seguridad	🔒 SEGURIDAD: La matriz de accesos y capacidades para el rol 'Analista' fue reconfigurada por Aileen Moyeja.	t	2026-07-14 09:23:06.815171
10	\N	Seguridad	Ecosistema: El privilegio técnico 'ver_formaciones' fue actualizado en el catálogo por Aileen Moyeja.	t	2026-07-14 09:23:46.401613
11	\N	Seguridad	¡CRÍTICO!: La cuenta de Perez Jimenes fue removida del sistema por el operador Aileen Moyeja.	t	2026-07-14 09:24:16.064339
12	\N	Usuarios	El operador Aileen Moyeja registró al nuevo usuario Angelo Martinez en la plataforma.	t	2026-07-14 09:29:09.711834
13	\N	Seguridad	Ecosistema: El privilegio técnico 'crear_divulgaciones' fue actualizado en el catálogo por Aileen Moyeja.	t	2026-07-14 21:45:52.529253
14	\N	Seguridad	Ecosistema: El privilegio técnico 'aprobar_divulgaciones' fue actualizado en el catálogo por Genghis Khan.	t	2026-07-14 21:46:59.391051
15	\N	Seguridad	Ecosistema: Se registró una nueva capacidad atómica en el catálogo global: 'gestionar_formaciones'.	t	2026-07-15 08:28:34.328233
16	\N	Seguridad	Ecosistema: Se registró una nueva capacidad atómica en el catálogo global: 'gestionar_sensibilizaciones'.	t	2026-07-15 08:29:01.196206
17	\N	Seguridad	Ecosistema: Se registró una nueva capacidad atómica en el catálogo global: 'registro_zenka'.	t	2026-07-15 08:31:02.223447
18	\N	Seguridad	⚠️ ATENCIÓN: El privilegio atómico 'registro_zenka' fue revocado y removido permanentemente del catálogo global.	t	2026-07-15 08:31:09.565008
19	\N	Seguridad	⚠️ ATENCIÓN: El privilegio atómico 'gestionar_sensibilizaciones' fue revocado y removido permanentemente del catálogo global.	t	2026-07-15 08:35:42.828684
20	\N	Seguridad	⚠️ ATENCIÓN: El privilegio atómico 'gestionar_formaciones' fue revocado y removido permanentemente del catálogo global.	t	2026-07-15 08:35:47.483427
21	\N	Seguridad	⚠️ ATENCIÓN: El privilegio atómico 'ver_formaciones' fue revocado y removido permanentemente del catálogo global.	t	2026-07-15 08:37:20.235862
22	\N	Seguridad	Ecosistema: Se registró una nueva capacidad atómica en el catálogo global: 'gestionar_inventario'.	t	2026-07-15 08:44:43.769958
23	\N	Seguridad	⚠️ ATENCIÓN: El privilegio atómico 'gestionar_inventario' fue revocado y removido permanentemente del catálogo global.	t	2026-07-15 08:51:27.872516
24	\N	Seguridad	Ecosistema: Se registró una nueva capacidad atómica en el catálogo global: 'gestionar_formaciones'.	t	2026-07-15 08:51:44.218961
25	\N	Seguridad	Ecosistema: Se registró una nueva capacidad atómica en el catálogo global: 'gestionar_sensibilizaciones'.	t	2026-07-15 08:52:09.424817
26	\N	Seguridad	Ecosistema: Se registró una nueva capacidad atómica en el catálogo global: 'gestionar_geomatica'.	t	2026-07-15 08:53:43.97628
27	\N	Seguridad	Ecosistema: Se registró una nueva capacidad atómica en el catálogo global: 'ver_mapas'.	t	2026-07-15 08:54:08.316476
28	\N	Seguridad	Ecosistema: Se registró una nueva capacidad atómica en el catálogo global: 'gestionar_inventario'.	t	2026-07-15 08:54:52.842323
29	\N	Seguridad	Ecosistema: Se registró una nueva capacidad atómica en el catálogo global: 'gestionar_tecnicos'.	t	2026-07-15 08:57:59.176223
30	\N	Seguridad	🔒 SEGURIDAD: La matriz de accesos y capacidades para el rol 'Tecnico' fue reconfigurada por Aileen Moyeja.	t	2026-07-15 08:58:50.573133
31	\N	Seguridad	🔒 SEGURIDAD: La matriz de accesos y capacidades para el rol 'Tecnico' fue reconfigurada por Aileen Moyeja.	t	2026-07-15 08:59:06.153428
32	\N	Seguridad	🔒 SEGURIDAD: La matriz de accesos y capacidades para el rol 'Tecnico' fue reconfigurada por Aileen Moyeja.	t	2026-07-15 09:03:07.273989
33	\N	Seguridad	🔒 SEGURIDAD: La matriz de accesos y capacidades para el rol 'Tecnico' fue reconfigurada por Aileen Moyeja.	t	2026-07-15 09:08:27.446813
34	\N	Seguridad	🔒 SEGURIDAD: La matriz de accesos y capacidades para el rol 'Tecnico' fue reconfigurada por Aileen Moyeja.	t	2026-07-15 09:14:42.086581
35	\N	Seguridad	🔒 SEGURIDAD: La matriz de accesos y capacidades para el rol 'Tecnico' fue reconfigurada por Aileen Moyeja.	t	2026-07-15 09:17:13.12807
36	\N	Seguridad	🔒 SEGURIDAD: La matriz de accesos y capacidades para el rol 'Tecnico' fue reconfigurada por Aileen Moyeja.	t	2026-07-15 09:19:55.070783
37	\N	Seguridad	🔒 SEGURIDAD: La matriz de accesos y capacidades para el rol 'Analista' fue reconfigurada por Aileen Moyeja.	t	2026-07-15 09:20:20.095663
38	\N	Seguridad	Ecosistema: Se registró una nueva capacidad atómica en el catálogo global: 'gestionar_actividades'.	t	2026-07-15 09:23:29.040349
39	\N	Seguridad	🔒 SEGURIDAD: La matriz de accesos y capacidades para el rol 'Tecnico' fue reconfigurada por Aileen Moyeja.	t	2026-07-15 09:25:38.551201
40	\N	Seguridad	🔒 SEGURIDAD: La matriz de accesos y capacidades para el rol 'Tecnico' fue reconfigurada por Aileen Moyeja.	t	2026-07-15 09:29:17.399739
41	\N	Sistema	Divulgación: El operador Aileen Moyeja registró un nuevo contenido bajo estatus 'borrador': 'Titulo de articulo...'.	f	2026-08-14 11:53:14.587628
\.


--
-- Data for Name: parroquia; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.parroquia (id_parroquia, id_municipio, nombre_parroquia) FROM stdin;
1	1	Catedral
\.


--
-- Data for Name: password_resets; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.password_resets (id, user_id, token, creado_en, expiracion, usado) FROM stdin;
1	13	wMjbVWGTgA4SrHRNEwCR67ncPO7XOZRE	2026-07-13 22:04:24.273241	2026-07-14 00:04:24.28342	t
2	19	GMf4ULcHWVmMxACDdAXgRByRUgBYSpjF	2026-07-13 23:15:42.461267	2026-07-14 01:15:42.461267	f
3	19	B-K9JIBlMTw7bHTBRXy2xUwAO7A7ExS2	2026-07-13 23:18:11.907581	2026-07-14 01:18:11.907581	f
4	19	CYkd1bwnB8tO3qXQEtiG2jfYEhqk-Olp	2026-07-13 23:19:30.027503	2026-07-14 01:19:30.178696	f
5	19	_TUSBTWPTlcHgFJwXPyzLYjedIZvsDOB	2026-07-13 23:20:16.126282	2026-07-14 01:20:16.128561	f
6	19	DtT3H3bOfegzrBMXzy0l-ssJloX79_Qx	2026-07-13 23:21:38.68525	2026-07-14 01:21:38.896452	f
7	19	pM5v2CqmWP_iX-OU2nj0IMj5GcabSiao	2026-07-13 23:24:31.835572	2026-07-14 01:24:32.027239	f
8	19	5CQwt4iYqZeAqqneI12DcaV9xhfk8nB1	2026-07-13 23:25:40.521727	2026-07-14 01:25:40.747612	f
9	19	Thmy-QA11Gf6FYBtyitNpqyJOTbkUW3T	2026-07-13 23:30:37.210828	2026-07-14 01:30:37.322095	f
10	19	jOZ2eeTkRiabzpudu_DKjRQVQ2SWjBq3	2026-07-13 23:39:49.105176	2026-07-14 01:39:49.202406	f
11	19	5Ca_JeYFElWZtEJ8W8T8mm5zG8tqB_sh	2026-07-14 00:03:33.030945	2026-07-14 02:03:33.147232	f
12	19	HIZ3YeaWJARclOQMVpIWm0aJHEmu7r4q	2026-07-14 00:09:54.2079	2026-07-14 02:09:54.391207	f
13	19	wL4eOKh974ogEajRru-lZnXFxgDpb0ms	2026-07-14 00:12:18.839225	2026-07-14 02:12:18.974208	f
14	19	9oyHoHhwk8AtpP5XQbUa6N7A5tm5Gpp8	2026-07-14 00:14:50.678757	2026-07-14 02:14:50.895287	f
15	19	TLo7BGkns8u1XDzsAhAzm_IugqwHvYRF	2026-07-14 00:15:03.89092	2026-07-14 02:15:03.89092	f
16	19	Vzd5PEpreKrLGhQMCMr8BoATLtfSB_RD	2026-07-14 00:15:22.007057	2026-07-14 02:15:22.106092	f
17	19	CP_bnGE9iP5b_eHRDC3CIymNYYg7u2uj	2026-07-14 00:17:16.251805	2026-07-14 02:17:16.389395	f
18	19	w8GwNau0ldjWEbc3LNVWreSzvEIxq4Qb	2026-07-14 00:18:31.963398	2026-07-14 02:18:31.963398	f
19	19	AuykwiZON2WxqLFsSPseZ36lTDXAyBOC	2026-07-14 00:20:40.61114	2026-07-14 02:20:41.322376	f
20	19	U-6rFHiCfUZc2Z3BILJZWbijaR0Dny1b	2026-07-14 00:21:01.699465	2026-07-14 02:21:01.703248	f
21	19	eoL1OOngKHx5Pj28g9MR5V5iKZ7r9bZG	2026-07-14 00:23:28.604287	2026-07-14 02:23:28.604287	f
22	19	vzmasL9XXesxO6qOZ10stD4c1D2XPq-_	2026-07-14 00:24:02.466876	2026-07-14 02:24:02.563972	f
23	19	Ctvrud361dYOOlVgm94emaQKWhUkrFDX	2026-07-14 00:24:30.306553	2026-07-14 02:24:30.405304	f
24	19	UDiSBPAV6h3HbX8536S30WJnPL7niCdd	2026-07-14 00:25:00.502052	2026-07-14 02:25:00.607467	f
25	19	h734tXQfGKPGUopWZrR1zzpMF6YEE8LV	2026-07-14 00:36:42.956242	2026-07-14 02:36:43.056179	f
\.


--
-- Data for Name: permiso; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.permiso (id_modulo, id_rol) FROM stdin;
\.


--
-- Data for Name: publicaciones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.publicaciones (id_publicacion, id_divulgacion, id_usuario, tipo, titulo_publicacion, membrete, resumen, contenido, estado_publicacion, fecha_publicacion, publicado_en, creado_en, actualizado_en, prioridad) FROM stdin;
4	1	4	informe	Titulo de articulo	\N	Resumen introductorio	Desarrolle el cuerpo del reporte.	publicado	2026-08-15	2026-08-14 11:53:42.111309	2026-08-14 07:53:14.540268	2026-08-14 07:53:42.103347	6
\.


--
-- Data for Name: registros_climaticos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.registros_climaticos (id_registro, fecha_registro, id_equipo, id_mapa_climatico, temperatura, precipitaciones, vientos, humedad) FROM stdin;
\.


--
-- Data for Name: reportes_transaccionales; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reportes_transaccionales (id, titulo, modulo_origen, rango_desde, rango_hasta, formato, estado, responsable, creado_en, actualizado_en) FROM stdin;
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id_rol, nombre_rol) FROM stdin;
\.


--
-- Data for Name: sensibilizacion; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sensibilizacion (id_sensibilizacion, id_actividad, nombre_sensibilizacion, tipo_actividad, id_nivel) FROM stdin;
2	17	Gestion de Desechos Solidos||Maria Perez	SENSIBILIZACION	1
\.


--
-- Data for Name: spatial_ref_sys; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) FROM stdin;
\.


--
-- Data for Name: tecnicos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tecnicos (id_tecnico, cedula, nombres, apellidos) FROM stdin;
1	V-12345678	Angel	Garc¡a
2	V-87654321	Aileen	Moyeja
3	V-11223344	Brayan	Aiden
\.


--
-- Data for Name: tema; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tema (id_tema, nombre_tema, descripcion_tema) FROM stdin;
\.


--
-- Data for Name: ubicacion; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ubicacion (id_ubicacion, id_parroquia, nombre_ubicacion) FROM stdin;
\.


--
-- Data for Name: usuario; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuario (id_usuario, nombre_usuario, "clave usuario", id_rol, correo, cedula, especialidad, estatus) FROM stdin;
\.


--
-- Data for Name: visitas_portal; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.visitas_portal (id, mes, creado_en) FROM stdin;
1	2026-06	2026-06-23 22:43:07.403984
2	2026-06	2026-06-23 23:45:25.555106
3	2026-06	2026-06-23 23:46:43.883074
4	2026-06	2026-06-23 23:46:59.508023
5	2026-06	2026-06-24 00:01:49.492089
6	2026-06	2026-06-24 00:04:13.456137
7	2026-06	2026-06-24 00:08:11.684021
8	2026-06	2026-06-24 00:08:13.888389
9	2026-06	2026-06-24 00:10:18.332543
10	2026-06	2026-06-24 00:13:14.68113
11	2026-06	2026-06-24 00:17:25.619916
12	2026-06	2026-06-24 00:20:50.807676
13	2026-06	2026-06-24 00:22:11.372916
14	2026-06	2026-06-25 00:29:26.092837
15	2026-06	2026-06-27 12:34:54.46264
16	2026-07	2026-07-08 00:10:09.302532
17	2026-07	2026-07-08 18:20:38.528376
18	2026-07	2026-07-09 04:43:03.361844
19	2026-07	2026-07-09 09:04:59.181115
20	2026-07	2026-07-09 15:02:10.086495
21	2026-07	2026-07-09 19:00:36.136803
22	2026-07	2026-07-10 11:34:46.040326
23	2026-07	2026-07-10 11:36:43.465493
24	2026-07	2026-07-10 13:12:14.039994
25	2026-07	2026-07-10 13:40:54.603891
26	2026-07	2026-07-10 18:53:58.475641
27	2026-07	2026-07-11 14:43:40.719943
28	2026-07	2026-07-13 15:18:31.278161
29	2026-07	2026-07-13 21:20:20.664766
30	2026-07	2026-07-14 02:01:10.593216
31	2026-07	2026-07-14 08:55:18.997032
32	2026-07	2026-07-14 15:16:45.688034
33	2026-07	2026-07-14 21:37:08.903488
34	2026-07	2026-07-15 01:05:05.38247
35	2026-07	2026-07-15 08:20:13.756911
36	2026-07	2026-07-15 14:21:05.387515
37	2026-07	2026-07-15 22:43:46.28753
38	2026-08	2026-08-12 22:16:27.071732
39	2026-08	2026-08-13 08:22:04.02248
40	2026-08	2026-08-13 21:09:47.589616
41	2026-08	2026-08-14 11:00:23.236988
42	2026-08	2026-08-14 13:12:06.336788
\.


--
-- Name: actividad_id_actividad_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.actividad_id_actividad_seq', 17, true);


--
-- Name: actividad_tecnico_id_actividad_tecnico_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.actividad_tecnico_id_actividad_tecnico_seq', 17, true);


--
-- Name: actividades_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.actividades_id_seq', 1, false);


--
-- Name: bitacora_transacciones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bitacora_transacciones_id_seq', 82, true);


--
-- Name: categoria_id_categoria_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.categoria_id_categoria_seq', 1, false);


--
-- Name: comunidad_id_comunidad_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.comunidad_id_comunidad_seq', 11, true);


--
-- Name: divulgacion_id_divulgacion_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.divulgacion_id_divulgacion_seq', 1, true);


--
-- Name: elemento_mapa_riesgo_id_elemento_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.elemento_mapa_riesgo_id_elemento_seq', 1, false);


--
-- Name: equipo_id_equipo_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.equipo_id_equipo_seq', 1, false);


--
-- Name: equipo_monitoreo_id_monitoreo_equipo_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.equipo_monitoreo_id_monitoreo_equipo_seq', 1, false);


--
-- Name: estado_id_estado_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.estado_id_estado_seq', 10, true);


--
-- Name: formacion_id_formacion_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.formacion_id_formacion_seq', 4, true);


--
-- Name: imagenes_actividad_id_imagenes_actividad_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.imagenes_actividad_id_imagenes_actividad_seq', 2, true);


--
-- Name: imagenes_id_imagen_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.imagenes_id_imagen_seq', 7, true);


--
-- Name: imagenes_publicacion_id_imagenes_publicacion_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.imagenes_publicacion_id_imagenes_publicacion_seq', 1, false);


--
-- Name: institucion_id_institucion_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.institucion_id_institucion_seq', 2, true);


--
-- Name: inventario_equipos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.inventario_equipos_id_seq', 1, false);


--
-- Name: mapa_climatico_id_mapa_climatico_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.mapa_climatico_id_mapa_climatico_seq', 1, false);


--
-- Name: mapa_riesgo_id_mapa_riesgo_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.mapa_riesgo_id_mapa_riesgo_seq', 1, false);


--
-- Name: mapas_registro_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.mapas_registro_id_seq', 1, false);


--
-- Name: material_id_material_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.material_id_material_seq', 1, false);


--
-- Name: modelos_equipo_id_modelos_equipo_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.modelos_equipo_id_modelos_equipo_seq', 1, false);


--
-- Name: modulos_id_modulo_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.modulos_id_modulo_seq', 1, false);


--
-- Name: monitoreo_id_monitoreo_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.monitoreo_id_monitoreo_seq', 7, true);


--
-- Name: movimientos_id_movimientos_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.movimientos_id_movimientos_seq', 1, false);


--
-- Name: municipio_id_municipio_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.municipio_id_municipio_seq', 10, true);


--
-- Name: nivel_id_nivel_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.nivel_id_nivel_seq', 4, true);


--
-- Name: notificaciones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.notificaciones_id_seq', 41, true);


--
-- Name: parroquia_id_parroquia_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.parroquia_id_parroquia_seq', 10, true);


--
-- Name: password_resets_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.password_resets_id_seq', 25, true);


--
-- Name: publicaciones_id_publicacion_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.publicaciones_id_publicacion_seq', 4, true);


--
-- Name: registros_climaticos_id_registro_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.registros_climaticos_id_registro_seq', 1, false);


--
-- Name: reportes_transaccionales_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reportes_transaccionales_id_seq', 1, false);


--
-- Name: roles_id_rol_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_rol_seq', 1, false);


--
-- Name: sensibilizacion_id_sensibilizacion_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sensibilizacion_id_sensibilizacion_seq', 2, true);


--
-- Name: tecnicos_id_tecnico_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tecnicos_id_tecnico_seq', 3, true);


--
-- Name: tema_id_tema_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tema_id_tema_seq', 1, false);


--
-- Name: ubicacion_id_ubicacion_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.ubicacion_id_ubicacion_seq', 1, false);


--
-- Name: usuario_id_usuario_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usuario_id_usuario_seq', 1, false);


--
-- Name: visitas_portal_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.visitas_portal_id_seq', 42, true);


--
-- Name: actividad actividad_id_y_tipo_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.actividad
    ADD CONSTRAINT actividad_id_y_tipo_key UNIQUE (id_actividad, tipo_actividad);


--
-- Name: actividad actividad_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.actividad
    ADD CONSTRAINT actividad_pkey PRIMARY KEY (id_actividad);


--
-- Name: actividad_tecnico actividad_tecnico_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.actividad_tecnico
    ADD CONSTRAINT actividad_tecnico_pkey PRIMARY KEY (id_actividad_tecnico);


--
-- Name: actividades actividades_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.actividades
    ADD CONSTRAINT actividades_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkey PRIMARY KEY (version_num);


--
-- Name: bitacora_transacciones bitacora_transacciones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bitacora_transacciones
    ADD CONSTRAINT bitacora_transacciones_pkey PRIMARY KEY (id);


--
-- Name: categoria categoria_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categoria
    ADD CONSTRAINT categoria_pkey PRIMARY KEY (id_categoria);


--
-- Name: comunidad comunidad_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comunidad
    ADD CONSTRAINT comunidad_pkey PRIMARY KEY (id_comunidad);


--
-- Name: divulgacion divulgacion_id_actividad_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.divulgacion
    ADD CONSTRAINT divulgacion_id_actividad_key UNIQUE (id_actividad);


--
-- Name: divulgacion divulgacion_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.divulgacion
    ADD CONSTRAINT divulgacion_pkey PRIMARY KEY (id_divulgacion);


--
-- Name: elemento_mapa_riesgo elemento_mapa_riesgo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.elemento_mapa_riesgo
    ADD CONSTRAINT elemento_mapa_riesgo_pkey PRIMARY KEY (id_elemento);


--
-- Name: equipo equipo_codigo_interno_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipo
    ADD CONSTRAINT equipo_codigo_interno_key UNIQUE (codigo_interno);


--
-- Name: equipo_monitoreo equipo_monitoreo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipo_monitoreo
    ADD CONSTRAINT equipo_monitoreo_pkey PRIMARY KEY (id_monitoreo_equipo);


--
-- Name: equipo equipo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipo
    ADD CONSTRAINT equipo_pkey PRIMARY KEY (id_equipo);


--
-- Name: estado estado_nombre_estado_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estado
    ADD CONSTRAINT estado_nombre_estado_key UNIQUE (nombre_estado);


--
-- Name: estado estado_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estado
    ADD CONSTRAINT estado_pkey PRIMARY KEY (id_estado);


--
-- Name: formacion formacion_id_actividad_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.formacion
    ADD CONSTRAINT formacion_id_actividad_key UNIQUE (id_actividad);


--
-- Name: formacion formacion_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.formacion
    ADD CONSTRAINT formacion_pkey PRIMARY KEY (id_formacion);


--
-- Name: imagenes_actividad imagenes_actividad_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.imagenes_actividad
    ADD CONSTRAINT imagenes_actividad_pkey PRIMARY KEY (id_imagenes_actividad);


--
-- Name: imagenes imagenes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.imagenes
    ADD CONSTRAINT imagenes_pkey PRIMARY KEY (id_imagen);


--
-- Name: imagenes_publicacion imagenes_publicacion_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.imagenes_publicacion
    ADD CONSTRAINT imagenes_publicacion_pkey PRIMARY KEY (id_imagenes_publicacion);


--
-- Name: institucion institucion_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.institucion
    ADD CONSTRAINT institucion_pkey PRIMARY KEY (id_institucion);


--
-- Name: inventario_equipos inventario_equipos_codigo_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventario_equipos
    ADD CONSTRAINT inventario_equipos_codigo_key UNIQUE (codigo);


--
-- Name: inventario_equipos inventario_equipos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventario_equipos
    ADD CONSTRAINT inventario_equipos_pkey PRIMARY KEY (id);


--
-- Name: mapa_climatico mapa_climatico_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mapa_climatico
    ADD CONSTRAINT mapa_climatico_pkey PRIMARY KEY (id_mapa_climatico);


--
-- Name: mapa_riesgo mapa_riesgo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mapa_riesgo
    ADD CONSTRAINT mapa_riesgo_pkey PRIMARY KEY (id_mapa_riesgo);


--
-- Name: mapas_registro mapas_registro_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mapas_registro
    ADD CONSTRAINT mapas_registro_pkey PRIMARY KEY (id);


--
-- Name: material material_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.material
    ADD CONSTRAINT material_pkey PRIMARY KEY (id_material);


--
-- Name: modelos_equipo modelos_equipo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modelos_equipo
    ADD CONSTRAINT modelos_equipo_pkey PRIMARY KEY (id_modelos_equipo);


--
-- Name: modulos modulos_nombre_modulo_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modulos
    ADD CONSTRAINT modulos_nombre_modulo_key UNIQUE (nombre_modulo);


--
-- Name: modulos modulos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modulos
    ADD CONSTRAINT modulos_pkey PRIMARY KEY (id_modulo);


--
-- Name: monitoreo monitoreo_id_actividad_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.monitoreo
    ADD CONSTRAINT monitoreo_id_actividad_key UNIQUE (id_actividad);


--
-- Name: monitoreo monitoreo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.monitoreo
    ADD CONSTRAINT monitoreo_pkey PRIMARY KEY (id_monitoreo);


--
-- Name: movimientos movimientos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movimientos
    ADD CONSTRAINT movimientos_pkey PRIMARY KEY (id_movimientos);


--
-- Name: municipio municipio_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.municipio
    ADD CONSTRAINT municipio_pkey PRIMARY KEY (id_municipio);


--
-- Name: nivel nivel_nombre_nivel_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nivel
    ADD CONSTRAINT nivel_nombre_nivel_key UNIQUE (nombre_nivel);


--
-- Name: nivel nivel_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nivel
    ADD CONSTRAINT nivel_pkey PRIMARY KEY (id_nivel);


--
-- Name: notificaciones notificaciones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notificaciones
    ADD CONSTRAINT notificaciones_pkey PRIMARY KEY (id);


--
-- Name: parroquia parroquia_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parroquia
    ADD CONSTRAINT parroquia_pkey PRIMARY KEY (id_parroquia);


--
-- Name: password_resets password_resets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_resets
    ADD CONSTRAINT password_resets_pkey PRIMARY KEY (id);


--
-- Name: password_resets password_resets_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_resets
    ADD CONSTRAINT password_resets_token_key UNIQUE (token);


--
-- Name: publicaciones publicaciones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.publicaciones
    ADD CONSTRAINT publicaciones_pkey PRIMARY KEY (id_publicacion);


--
-- Name: registros_climaticos registros_climaticos_fecha_registro_id_equipo_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registros_climaticos
    ADD CONSTRAINT registros_climaticos_fecha_registro_id_equipo_key UNIQUE (fecha_registro, id_equipo);


--
-- Name: registros_climaticos registros_climaticos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registros_climaticos
    ADD CONSTRAINT registros_climaticos_pkey PRIMARY KEY (id_registro, fecha_registro);


--
-- Name: reportes_transaccionales reportes_transaccionales_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reportes_transaccionales
    ADD CONSTRAINT reportes_transaccionales_pkey PRIMARY KEY (id);


--
-- Name: roles roles_nombre_rol_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_nombre_rol_key UNIQUE (nombre_rol);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id_rol);


--
-- Name: sensibilizacion sensibilizacion_id_actividad_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sensibilizacion
    ADD CONSTRAINT sensibilizacion_id_actividad_key UNIQUE (id_actividad);


--
-- Name: sensibilizacion sensibilizacion_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sensibilizacion
    ADD CONSTRAINT sensibilizacion_pkey PRIMARY KEY (id_sensibilizacion);


--
-- Name: tecnicos tecnicos_cedula_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tecnicos
    ADD CONSTRAINT tecnicos_cedula_key UNIQUE (cedula);


--
-- Name: tecnicos tecnicos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tecnicos
    ADD CONSTRAINT tecnicos_pkey PRIMARY KEY (id_tecnico);


--
-- Name: tema tema_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tema
    ADD CONSTRAINT tema_pkey PRIMARY KEY (id_tema);


--
-- Name: ubicacion ubicacion_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ubicacion
    ADD CONSTRAINT ubicacion_pkey PRIMARY KEY (id_ubicacion);


--
-- Name: usuario usuario_cedula_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_cedula_key UNIQUE (cedula);


--
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (id_usuario);


--
-- Name: visitas_portal visitas_portal_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.visitas_portal
    ADD CONSTRAINT visitas_portal_pkey PRIMARY KEY (id);


--
-- Name: idx_act_tec_actividad; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_act_tec_actividad ON public.actividad_tecnico USING btree (id_actividad);


--
-- Name: idx_act_tec_tecnico; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_act_tec_tecnico ON public.actividad_tecnico USING btree (id_tecnico);


--
-- Name: idx_actividad_comunidad; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_actividad_comunidad ON public.actividad USING btree (id_comunidad);


--
-- Name: idx_comunidad_parroquia; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_comunidad_parroquia ON public.comunidad USING btree (id_parroquia);


--
-- Name: idx_elemento_mapa_riesgo_geom; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_elemento_mapa_riesgo_geom ON public.elemento_mapa_riesgo USING gist (geometria);


--
-- Name: idx_eq_monitoreo_equipo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_eq_monitoreo_equipo ON public.equipo_monitoreo USING btree (id_equipo);


--
-- Name: idx_eq_monitoreo_monitoreo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_eq_monitoreo_monitoreo ON public.equipo_monitoreo USING btree (id_monitoreo);


--
-- Name: idx_equipo_modelo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_equipo_modelo ON public.equipo USING btree (id_modelos_equipos);


--
-- Name: idx_equipo_ubicacion_actual; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_equipo_ubicacion_actual ON public.equipo USING btree (id_ubicacion_actual);


--
-- Name: idx_formacion_institucion; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_formacion_institucion ON public.formacion USING btree (id_institucion);


--
-- Name: idx_img_act_actividad; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_img_act_actividad ON public.imagenes_actividad USING btree (id_actividad);


--
-- Name: idx_img_act_imagen; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_img_act_imagen ON public.imagenes_actividad USING btree (id_imagen);


--
-- Name: idx_img_pub_imagen; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_img_pub_imagen ON public.imagenes_publicacion USING btree (id_imagen);


--
-- Name: idx_img_pub_publicacion; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_img_pub_publicacion ON public.imagenes_publicacion USING btree (id_publicacion);


--
-- Name: idx_institucion_comunidad; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_institucion_comunidad ON public.institucion USING btree (id_comunidad);


--
-- Name: idx_mapacli_municipio; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_mapacli_municipio ON public.mapa_climatico USING btree (id_municipio);


--
-- Name: idx_maparies_actividad; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_maparies_actividad ON public.mapa_riesgo USING btree (id_actividad);


--
-- Name: idx_material_nivel; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_material_nivel ON public.material USING btree (id_nivel);


--
-- Name: idx_material_tema; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_material_tema ON public.material USING btree (id_tema);


--
-- Name: idx_modelos_categoria; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_modelos_categoria ON public.modelos_equipo USING btree (id_categoria);


--
-- Name: idx_movimientos_equipo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_movimientos_equipo ON public.movimientos USING btree (id_equipo);


--
-- Name: idx_movimientos_ubic_destino; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_movimientos_ubic_destino ON public.movimientos USING btree (id_ubicacion_destino);


--
-- Name: idx_movimientos_ubic_origen; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_movimientos_ubic_origen ON public.movimientos USING btree (id_ubicacion_origen);


--
-- Name: idx_municipio_estado; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_municipio_estado ON public.municipio USING btree (id_estado);


--
-- Name: idx_parroquia_municipio; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_parroquia_municipio ON public.parroquia USING btree (id_municipio);


--
-- Name: idx_publicaciones_divulgacion; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_publicaciones_divulgacion ON public.publicaciones USING btree (id_divulgacion);


--
-- Name: idx_regcli_equipo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_regcli_equipo ON public.registros_climaticos USING btree (id_equipo);


--
-- Name: idx_regcli_mapa; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_regcli_mapa ON public.registros_climaticos USING btree (id_mapa_climatico);


--
-- Name: idx_ubicacion_parroquia; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_ubicacion_parroquia ON public.ubicacion USING btree (id_parroquia);


--
-- Name: mapa_riesgo tg_validar_sensibilizacion_previa; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tg_validar_sensibilizacion_previa BEFORE INSERT OR UPDATE ON public.mapa_riesgo FOR EACH ROW EXECUTE FUNCTION public.validar_previa_sensibilizacion();


--
-- Name: actividad actividad_id_comunidad_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.actividad
    ADD CONSTRAINT actividad_id_comunidad_fkey FOREIGN KEY (id_comunidad) REFERENCES public.comunidad(id_comunidad) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: actividad_tecnico actividad_tecnico_id_actividad_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.actividad_tecnico
    ADD CONSTRAINT actividad_tecnico_id_actividad_fkey FOREIGN KEY (id_actividad) REFERENCES public.actividad(id_actividad) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: actividad_tecnico actividad_tecnico_id_tecnico_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.actividad_tecnico
    ADD CONSTRAINT actividad_tecnico_id_tecnico_fkey FOREIGN KEY (id_tecnico) REFERENCES public.tecnicos(id_tecnico) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: comunidad comunidad_id_parroquia_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comunidad
    ADD CONSTRAINT comunidad_id_parroquia_fkey FOREIGN KEY (id_parroquia) REFERENCES public.parroquia(id_parroquia) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: divulgacion divulgacion_id_actividad_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.divulgacion
    ADD CONSTRAINT divulgacion_id_actividad_fkey FOREIGN KEY (id_actividad) REFERENCES public.actividad(id_actividad) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: elemento_mapa_riesgo elemento_mapa_riesgo_id_mapa_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.elemento_mapa_riesgo
    ADD CONSTRAINT elemento_mapa_riesgo_id_mapa_fkey FOREIGN KEY (id_mapa_riesgo) REFERENCES public.mapa_riesgo(id_mapa_riesgo) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: equipo equipo_id_modelos_equipos_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipo
    ADD CONSTRAINT equipo_id_modelos_equipos_fkey FOREIGN KEY (id_modelos_equipos) REFERENCES public.modelos_equipo(id_modelos_equipo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: equipo equipo_id_ubicacion_actual_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipo
    ADD CONSTRAINT equipo_id_ubicacion_actual_fkey FOREIGN KEY (id_ubicacion_actual) REFERENCES public.ubicacion(id_ubicacion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: equipo_monitoreo equipo_monitoreo_id_equipo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipo_monitoreo
    ADD CONSTRAINT equipo_monitoreo_id_equipo_fkey FOREIGN KEY (id_equipo) REFERENCES public.equipo(id_equipo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: equipo_monitoreo equipo_monitoreo_id_monitoreo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipo_monitoreo
    ADD CONSTRAINT equipo_monitoreo_id_monitoreo_fkey FOREIGN KEY (id_monitoreo) REFERENCES public.monitoreo(id_monitoreo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: actividad fk_actividad_nivel; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.actividad
    ADD CONSTRAINT fk_actividad_nivel FOREIGN KEY (id_nivel) REFERENCES public.nivel(id_nivel);


--
-- Name: formacion formacion_actividad_compuesta_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.formacion
    ADD CONSTRAINT formacion_actividad_compuesta_fkey FOREIGN KEY (id_actividad, tipo_actividad) REFERENCES public.actividad(id_actividad, tipo_actividad) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: formacion formacion_id_institucion_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.formacion
    ADD CONSTRAINT formacion_id_institucion_fkey FOREIGN KEY (id_institucion) REFERENCES public.institucion(id_institucion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: formacion formacion_id_nivel_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.formacion
    ADD CONSTRAINT formacion_id_nivel_fkey FOREIGN KEY (id_nivel) REFERENCES public.nivel(id_nivel) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: imagenes_actividad imagenes_actividad_id_actividad_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.imagenes_actividad
    ADD CONSTRAINT imagenes_actividad_id_actividad_fkey FOREIGN KEY (id_actividad) REFERENCES public.actividad(id_actividad) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: imagenes_actividad imagenes_actividad_id_imagen_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.imagenes_actividad
    ADD CONSTRAINT imagenes_actividad_id_imagen_fkey FOREIGN KEY (id_imagen) REFERENCES public.imagenes(id_imagen) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: imagenes_publicacion imagenes_publicacion_id_imagen_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.imagenes_publicacion
    ADD CONSTRAINT imagenes_publicacion_id_imagen_fkey FOREIGN KEY (id_imagen) REFERENCES public.imagenes(id_imagen) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: imagenes_publicacion imagenes_publicacion_id_publicacion_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.imagenes_publicacion
    ADD CONSTRAINT imagenes_publicacion_id_publicacion_fkey FOREIGN KEY (id_publicacion) REFERENCES public.publicaciones(id_publicacion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: institucion institucion_id_comunidad_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.institucion
    ADD CONSTRAINT institucion_id_comunidad_fkey FOREIGN KEY (id_comunidad) REFERENCES public.comunidad(id_comunidad) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: mapa_climatico mapa_climatico_id_municipio_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mapa_climatico
    ADD CONSTRAINT mapa_climatico_id_municipio_fkey FOREIGN KEY (id_municipio) REFERENCES public.municipio(id_municipio) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: mapa_riesgo mapa_riesgo_actividad_compuesta_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mapa_riesgo
    ADD CONSTRAINT mapa_riesgo_actividad_compuesta_fkey FOREIGN KEY (id_actividad, tipo_actividad) REFERENCES public.actividad(id_actividad, tipo_actividad) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: material material_id_nivel_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.material
    ADD CONSTRAINT material_id_nivel_fkey FOREIGN KEY (id_nivel) REFERENCES public.nivel(id_nivel) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: material material_id_tema_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.material
    ADD CONSTRAINT material_id_tema_fkey FOREIGN KEY (id_tema) REFERENCES public.tema(id_tema) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: modelos_equipo modelos_equipo_id_categoria_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modelos_equipo
    ADD CONSTRAINT modelos_equipo_id_categoria_fkey FOREIGN KEY (id_categoria) REFERENCES public.categoria(id_categoria) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: monitoreo monitoreo_actividad_compuesta_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.monitoreo
    ADD CONSTRAINT monitoreo_actividad_compuesta_fkey FOREIGN KEY (id_actividad, tipo_actividad) REFERENCES public.actividad(id_actividad, tipo_actividad) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: movimientos movimientos_id_equipo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movimientos
    ADD CONSTRAINT movimientos_id_equipo_fkey FOREIGN KEY (id_equipo) REFERENCES public.equipo(id_equipo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: movimientos movimientos_id_ubicacion_destino_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movimientos
    ADD CONSTRAINT movimientos_id_ubicacion_destino_fkey FOREIGN KEY (id_ubicacion_destino) REFERENCES public.ubicacion(id_ubicacion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: movimientos movimientos_id_ubicacion_origen_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movimientos
    ADD CONSTRAINT movimientos_id_ubicacion_origen_fkey FOREIGN KEY (id_ubicacion_origen) REFERENCES public.ubicacion(id_ubicacion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: municipio municipio_id_estado_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.municipio
    ADD CONSTRAINT municipio_id_estado_fkey FOREIGN KEY (id_estado) REFERENCES public.estado(id_estado) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: parroquia parroquia_id_municipio_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parroquia
    ADD CONSTRAINT parroquia_id_municipio_fkey FOREIGN KEY (id_municipio) REFERENCES public.municipio(id_municipio) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: permiso permiso_id_modulo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permiso
    ADD CONSTRAINT permiso_id_modulo_fkey FOREIGN KEY (id_modulo) REFERENCES public.modulos(id_modulo);


--
-- Name: permiso permiso_id_rol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permiso
    ADD CONSTRAINT permiso_id_rol_fkey FOREIGN KEY (id_rol) REFERENCES public.roles(id_rol);


--
-- Name: publicaciones publicaciones_id_divulgacion_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.publicaciones
    ADD CONSTRAINT publicaciones_id_divulgacion_fkey FOREIGN KEY (id_divulgacion) REFERENCES public.divulgacion(id_divulgacion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: registros_climaticos registros_climaticos_id_equipo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registros_climaticos
    ADD CONSTRAINT registros_climaticos_id_equipo_fkey FOREIGN KEY (id_equipo) REFERENCES public.equipo(id_equipo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: registros_climaticos registros_climaticos_id_mapa_climatico_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registros_climaticos
    ADD CONSTRAINT registros_climaticos_id_mapa_climatico_fkey FOREIGN KEY (id_mapa_climatico) REFERENCES public.mapa_climatico(id_mapa_climatico) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: sensibilizacion sensibilizacion_actividad_compuesta_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sensibilizacion
    ADD CONSTRAINT sensibilizacion_actividad_compuesta_fkey FOREIGN KEY (id_actividad, tipo_actividad) REFERENCES public.actividad(id_actividad, tipo_actividad) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: sensibilizacion sensibilizacion_id_nivel_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sensibilizacion
    ADD CONSTRAINT sensibilizacion_id_nivel_fkey FOREIGN KEY (id_nivel) REFERENCES public.nivel(id_nivel) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: ubicacion ubicacion_id_parroquia_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ubicacion
    ADD CONSTRAINT ubicacion_id_parroquia_fkey FOREIGN KEY (id_parroquia) REFERENCES public.parroquia(id_parroquia) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- PostgreSQL database dump complete
--

\unrestrict KV8z7ZB8lSY9t9q7cevsvleW97fFcdhHPg6YWyL2rRLtChgc8MVkYaqt47f1yzU

