--
-- PostgreSQL database dump
--

\restrict xVLOjulw3reXq9N8V8nUHByHQ45fhao7x24dX0OgdG9k87QUNNQHsAsQ3PBawvP

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
    id_comunidad integer NOT NULL
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
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

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
-- Name: mapa_climatico id_mapa_climatico; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mapa_climatico ALTER COLUMN id_mapa_climatico SET DEFAULT nextval('public.mapa_climatico_id_mapa_climatico_seq'::regclass);


--
-- Name: mapa_riesgo id_mapa_riesgo; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mapa_riesgo ALTER COLUMN id_mapa_riesgo SET DEFAULT nextval('public.mapa_riesgo_id_mapa_riesgo_seq'::regclass);


--
-- Name: material id_material; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.material ALTER COLUMN id_material SET DEFAULT nextval('public.material_id_material_seq'::regclass);


--
-- Name: modelos_equipo id_modelos_equipo; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modelos_equipo ALTER COLUMN id_modelos_equipo SET DEFAULT nextval('public.modelos_equipo_id_modelos_equipo_seq'::regclass);


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
-- Name: parroquia id_parroquia; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parroquia ALTER COLUMN id_parroquia SET DEFAULT nextval('public.parroquia_id_parroquia_seq'::regclass);


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
-- Name: visitas_portal id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.visitas_portal ALTER COLUMN id SET DEFAULT nextval('public.visitas_portal_id_seq'::regclass);


--
-- Data for Name: actividad; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.actividad (id_actividad, fecha_actividad, tipo_actividad, id_comunidad) FROM stdin;
\.


--
-- Data for Name: actividad_tecnico; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.actividad_tecnico (id_actividad_tecnico, id_actividad, id_tecnico) FROM stdin;
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
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
\.


--
-- Data for Name: divulgacion; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.divulgacion (id_divulgacion, id_actividad, nombre_divulgacion, descripcion_divulgacion, permiso_divulgacion) FROM stdin;
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
\.


--
-- Data for Name: formacion; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.formacion (id_formacion, id_actividad, id_institucion, nombre_formacion, tipo_actividad, id_nivel) FROM stdin;
\.


--
-- Data for Name: imagenes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.imagenes (id_imagen, url_imagen, nombre_imagen, fecha_imagen) FROM stdin;
\.


--
-- Data for Name: imagenes_actividad; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.imagenes_actividad (id_imagenes_actividad, id_imagen, id_actividad) FROM stdin;
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
\.


--
-- Data for Name: mapa_climatico; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mapa_climatico (id_mapa_climatico, id_municipio, tipo_de_mapa, url_mapa, fecha_creacion) FROM stdin;
\.


--
-- Data for Name: mapa_riesgo; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mapa_riesgo (id_mapa_riesgo, id_actividad, tipo_actividad, ruta_kml, ruta_imagen_mapa, fecha_registro) FROM stdin;
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
-- Data for Name: monitoreo; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.monitoreo (id_monitoreo, id_actividad, nombre_monitoreo, tipo_actividad) FROM stdin;
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
\.


--
-- Data for Name: nivel; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.nivel (id_nivel, nombre_nivel, descripcion) FROM stdin;
\.


--
-- Data for Name: parroquia; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.parroquia (id_parroquia, id_municipio, nombre_parroquia) FROM stdin;
\.


--
-- Data for Name: publicaciones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.publicaciones (id_publicacion, id_divulgacion, id_usuario, tipo, titulo_publicacion, membrete, resumen, contenido, estado_publicacion, fecha_publicacion, publicado_en, creado_en, actualizado_en, prioridad) FROM stdin;
2	\N	1	Boletin Especial	ALERTA MAXIMA: Riesgo de Inundacion Critica por Lluvias en Zonas Vulnerables	Observatorio Nacional de la Crisis Clim tica	Se registra un nivel critico de saturacion de suelos tras precipitaciones continuas.	Cuerpo del informe tecnico institucional del ONCC detallando las medidas de seguridad y monitoreo...	publicado	2026-06-23	2026-06-23 21:33:34.458368	2026-06-23 21:33:34.458368	2026-06-23 21:33:34.458368	10
3	\N	1	Reporte de Rutina	Monitoreo Institucional: Condiciones Climaticas Estables en la Region	Observatorio Nacional de la Crisis Clim tica	Se reportan cielos parcialmente nublados y precipitaciones d‚biles aisladas sin riesgo inminente.	Cuerpo del informe mensual del ONCC donde se constata que los niveles de los principales caudales se mantienen bajo los limites de seguridad.	publicado	2026-06-23	2026-06-23 21:35:06.485096	2026-06-23 21:35:06.485096	2026-06-23 21:35:06.485096	4
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
-- Data for Name: sensibilizacion; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sensibilizacion (id_sensibilizacion, id_actividad, nombre_sensibilizacion, tipo_actividad, id_nivel) FROM stdin;
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
\.


--
-- Name: actividad_id_actividad_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.actividad_id_actividad_seq', 1, false);


--
-- Name: actividad_tecnico_id_actividad_tecnico_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.actividad_tecnico_id_actividad_tecnico_seq', 1, false);


--
-- Name: categoria_id_categoria_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.categoria_id_categoria_seq', 1, false);


--
-- Name: comunidad_id_comunidad_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.comunidad_id_comunidad_seq', 3, true);


--
-- Name: divulgacion_id_divulgacion_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.divulgacion_id_divulgacion_seq', 1, false);


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

SELECT pg_catalog.setval('public.estado_id_estado_seq', 3, true);


--
-- Name: formacion_id_formacion_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.formacion_id_formacion_seq', 1, false);


--
-- Name: imagenes_actividad_id_imagenes_actividad_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.imagenes_actividad_id_imagenes_actividad_seq', 1, false);


--
-- Name: imagenes_id_imagen_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.imagenes_id_imagen_seq', 1, false);


--
-- Name: imagenes_publicacion_id_imagenes_publicacion_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.imagenes_publicacion_id_imagenes_publicacion_seq', 1, false);


--
-- Name: institucion_id_institucion_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.institucion_id_institucion_seq', 1, false);


--
-- Name: mapa_climatico_id_mapa_climatico_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.mapa_climatico_id_mapa_climatico_seq', 1, false);


--
-- Name: mapa_riesgo_id_mapa_riesgo_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.mapa_riesgo_id_mapa_riesgo_seq', 1, false);


--
-- Name: material_id_material_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.material_id_material_seq', 1, false);


--
-- Name: modelos_equipo_id_modelos_equipo_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.modelos_equipo_id_modelos_equipo_seq', 1, false);


--
-- Name: monitoreo_id_monitoreo_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.monitoreo_id_monitoreo_seq', 1, false);


--
-- Name: movimientos_id_movimientos_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.movimientos_id_movimientos_seq', 1, false);


--
-- Name: municipio_id_municipio_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.municipio_id_municipio_seq', 3, true);


--
-- Name: nivel_id_nivel_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.nivel_id_nivel_seq', 1, false);


--
-- Name: parroquia_id_parroquia_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.parroquia_id_parroquia_seq', 3, true);


--
-- Name: publicaciones_id_publicacion_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.publicaciones_id_publicacion_seq', 3, true);


--
-- Name: registros_climaticos_id_registro_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.registros_climaticos_id_registro_seq', 1, false);


--
-- Name: reportes_transaccionales_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reportes_transaccionales_id_seq', 1, false);


--
-- Name: sensibilizacion_id_sensibilizacion_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sensibilizacion_id_sensibilizacion_seq', 1, false);


--
-- Name: tecnicos_id_tecnico_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tecnicos_id_tecnico_seq', 1, false);


--
-- Name: tema_id_tema_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tema_id_tema_seq', 1, false);


--
-- Name: ubicacion_id_ubicacion_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.ubicacion_id_ubicacion_seq', 1, false);


--
-- Name: visitas_portal_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.visitas_portal_id_seq', 14, true);


--
-- Name: actividad actividad_fecha_actividad_tipo_actividad_id_comunidad_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.actividad
    ADD CONSTRAINT actividad_fecha_actividad_tipo_actividad_id_comunidad_key UNIQUE (fecha_actividad, tipo_actividad, id_comunidad);


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
-- Name: alembic_version alembic_version_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkey PRIMARY KEY (version_num);


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
-- Name: parroquia parroquia_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parroquia
    ADD CONSTRAINT parroquia_pkey PRIMARY KEY (id_parroquia);


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

\unrestrict xVLOjulw3reXq9N8V8nUHByHQ45fhao7x24dX0OgdG9k87QUNNQHsAsQ3PBawvP

