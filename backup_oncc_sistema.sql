--
-- PostgreSQL database dump
--

\restrict egLdFXOyq8F9tUp5pBRDMftm2fkLkJqGghTLH7UMUMhfB3QSNRMm1fyPu1OK86u

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
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO postgres;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS '';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: actividad; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.actividad (
    id_actividad integer NOT NULL,
    fecha_actividad date NOT NULL,
    tipo_actividad character varying(20)[] NOT NULL,
    id_comunidad integer NOT NULL,
    id_nivel integer NOT NULL,
    id_usuario integer
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
    nombre_formacion text NOT NULL,
    id_actividad integer NOT NULL,
    id_institucion integer NOT NULL
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
-- Name: institucion; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.institucion (
    id_institucion integer NOT NULL,
    id_comunidad integer NOT NULL,
    nombre_institucion character varying(50) NOT NULL,
    tipo_institucion character varying(20) NOT NULL,
    direccion_exacta character varying(100) NOT NULL,
    numero_contacto character varying(25) NOT NULL,
    correo_electronico character varying(40) NOT NULL
);


ALTER TABLE public.institucion OWNER TO postgres;

--
-- Name: intitucion_id_institucion_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.intitucion_id_institucion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.intitucion_id_institucion_seq OWNER TO postgres;

--
-- Name: intitucion_id_institucion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.intitucion_id_institucion_seq OWNED BY public.institucion.id_institucion;


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
    actualizado_en timestamp without time zone NOT NULL,
    numero_serie character varying(100),
    marca character varying(50),
    modelo character varying(50),
    observaciones text,
    id_usuario integer
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
    actualizado_en timestamp without time zone NOT NULL,
    id_parroquia integer
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
    "descripción " text NOT NULL
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
    id integer NOT NULL,
    tipo character varying(40) NOT NULL,
    titulo character varying(180) NOT NULL,
    resumen text,
    contenido text,
    estado character varying(20) NOT NULL,
    publicado_en timestamp without time zone,
    creado_en timestamp without time zone NOT NULL,
    actualizado_en timestamp without time zone NOT NULL,
    id_usuario integer NOT NULL,
    id_divulgacion integer,
    prioridad integer DEFAULT 1
);


ALTER TABLE public.publicaciones OWNER TO postgres;

--
-- Name: publicaciones_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.publicaciones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.publicaciones_id_seq OWNER TO postgres;

--
-- Name: publicaciones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.publicaciones_id_seq OWNED BY public.publicaciones.id;


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
    creado_en timestamp without time zone NOT NULL,
    actualizado_en timestamp without time zone NOT NULL
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
    id_sensivilizacion integer NOT NULL,
    nombre_sensivilizacion text NOT NULL,
    id_actividad integer NOT NULL
);


ALTER TABLE public.sensibilizacion OWNER TO postgres;

--
-- Name: sensibilizacion _id_sensivilizacion_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."sensibilizacion _id_sensivilizacion_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."sensibilizacion _id_sensivilizacion_seq" OWNER TO postgres;

--
-- Name: sensibilizacion _id_sensivilizacion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."sensibilizacion _id_sensivilizacion_seq" OWNED BY public.sensibilizacion.id_sensivilizacion;


--
-- Name: tecnicos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tecnicos (
    id_tecnico integer NOT NULL,
    cedula character varying(15) NOT NULL,
    nombres character varying(60) NOT NULL,
    apellidos character varying(60) NOT NULL,
    id_usuario integer
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
-- Name: temas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.temas (
    id_tema integer NOT NULL,
    nombre_tema character varying(100) NOT NULL,
    descripcion_tema text
);


ALTER TABLE public.temas OWNER TO postgres;

--
-- Name: temas_id_tema_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.temas_id_tema_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.temas_id_tema_seq OWNER TO postgres;

--
-- Name: temas_id_tema_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.temas_id_tema_seq OWNED BY public.temas.id_tema;


--
-- Name: usuario; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuario (
    id_usuario integer NOT NULL,
    nombre_usuario character varying(30) NOT NULL,
    "clave usuario" character varying(255) NOT NULL
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
    creado_en timestamp without time zone NOT NULL
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
-- Name: bitacora_transacciones id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bitacora_transacciones ALTER COLUMN id SET DEFAULT nextval('public.bitacora_transacciones_id_seq'::regclass);


--
-- Name: comunidad id_comunidad; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comunidad ALTER COLUMN id_comunidad SET DEFAULT nextval('public.comunidad_id_comunidad_seq'::regclass);


--
-- Name: divulgacion id_divulgacion; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.divulgacion ALTER COLUMN id_divulgacion SET DEFAULT nextval('public.divulgacion_id_divulgacion_seq'::regclass);


--
-- Name: estado id_estado; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estado ALTER COLUMN id_estado SET DEFAULT nextval('public.estado_id_estado_seq'::regclass);


--
-- Name: formacion id_formacion; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.formacion ALTER COLUMN id_formacion SET DEFAULT nextval('public.formacion_id_formacion_seq'::regclass);


--
-- Name: institucion id_institucion; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.institucion ALTER COLUMN id_institucion SET DEFAULT nextval('public.intitucion_id_institucion_seq'::regclass);


--
-- Name: inventario_equipos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventario_equipos ALTER COLUMN id SET DEFAULT nextval('public.inventario_equipos_id_seq'::regclass);


--
-- Name: mapas_registro id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mapas_registro ALTER COLUMN id SET DEFAULT nextval('public.mapas_registro_id_seq'::regclass);


--
-- Name: modulos id_modulo; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modulos ALTER COLUMN id_modulo SET DEFAULT nextval('public.modulos_id_modulo_seq'::regclass);


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
-- Name: publicaciones id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.publicaciones ALTER COLUMN id SET DEFAULT nextval('public.publicaciones_id_seq'::regclass);


--
-- Name: reportes_transaccionales id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reportes_transaccionales ALTER COLUMN id SET DEFAULT nextval('public.reportes_transaccionales_id_seq'::regclass);


--
-- Name: sensibilizacion id_sensivilizacion; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sensibilizacion ALTER COLUMN id_sensivilizacion SET DEFAULT nextval('public."sensibilizacion _id_sensivilizacion_seq"'::regclass);


--
-- Name: tecnicos id_tecnico; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tecnicos ALTER COLUMN id_tecnico SET DEFAULT nextval('public.tecnicos_id_tecnico_seq'::regclass);


--
-- Name: temas id_tema; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.temas ALTER COLUMN id_tema SET DEFAULT nextval('public.temas_id_tema_seq'::regclass);


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

COPY public.actividad (id_actividad, fecha_actividad, tipo_actividad, id_comunidad, id_nivel, id_usuario) FROM stdin;
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
782178008bd1
\.


--
-- Data for Name: bitacora_transacciones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bitacora_transacciones (id, modulo, registro_id, accion, estado_nuevo, usuario, detalle, creado_en) FROM stdin;
1	Usuarios	2	Crear	Técnico	director@oncc.gob.ve	Creado usuario maruchan@gmail.com	2026-06-07 16:51:55.413082
2	Usuarios	2	Modificar	Técnico	director@oncc.gob.ve	Editado usuario Mariangel	2026-06-07 16:52:18.530529
3	Usuarios	2	Eliminar	\N	director@oncc.gob.ve	Eliminado usuario Mariangel	2026-06-07 17:06:04.549983
4	Usuarios	3	Crear	Técnico	director@oncc.gob.ve	Creado usuario maruchan@gmail.com	2026-06-07 17:06:36.593086
5	Usuarios	3	Modificar	Técnico	director@oncc.gob.ve	Editado usuario Mariangel Reyes	2026-06-07 17:11:38.11326
6	Usuarios	3	Modificar	Técnico	director@oncc.gob.ve	Editado usuario Mariangel R	2026-06-07 17:38:05.192455
7	Usuarios	3	Modificar	Técnico	director@oncc.gob.ve	Editado usuario Mariangel Reyes	2026-06-07 17:54:39.704042
8	Usuarios	4	Crear	Administrador	director@oncc.gob.ve	Creado usuario sanches@gmail.com	2026-06-07 17:55:14.577315
9	Usuarios	4	Modificar	Administrador	director@oncc.gob.ve	Editado usuario sanchez	2026-06-07 17:57:06.115102
10	Usuarios	4	Modificar	Administrador	director@oncc.gob.ve	Editado usuario sanch	2026-06-07 18:10:29.419168
11	Usuarios	4	Modificar	Administrador	director@oncc.gob.ve	Editado usuario sanchesss	2026-06-07 18:14:58.555084
12	Usuarios	6	Crear	Administrador	director@oncc.gob.ve	Creado usuario d@gmail.com	2026-06-07 19:13:42.739032
13	Usuarios	4	Eliminar	\N	director@oncc.gob.ve	Eliminado usuario None	2026-06-07 19:19:45.570909
14	Usuarios	6	Modificar	Técnico	Director	Editado usuario d@gmail.com	2026-06-07 19:24:07.274613
15	Usuarios	6	Eliminar	\N	Director	Eliminado usuario d@gmail.com	2026-06-07 22:29:10.944311
16	Usuarios	3	Eliminar	\N	Director	Eliminado usuario sanchez@oncc.gob.ve	2026-06-07 22:29:27.587272
17	Usuarios	7	Crear	Técnico	Director	Creado usuario maruchan@gmail.com	2026-06-07 22:30:21.570609
18	Usuarios	8	Crear	Administrador	Director	Creado usuario moyejada@gmail.com	2026-06-07 22:31:08.459992
19	Usuarios	9	Crear	Técnico	Director	Creado usuario ferarri@gmail.com	2026-06-07 22:31:44.228089
20	Usuarios	10	Crear	Administrador	Director	Creado usuario gabrilucho@gmail.com	2026-06-07 22:33:17.58571
21	Usuarios	1	Modificar	Director Regional	Director	Editado usuario director@oncc.gob.ve	2026-06-07 23:43:53.127196
22	Divulgación	3	Crear	borrador	Aileen Moyeja	Creado contenido informativo: Taller de Crisis Climática en Quíbor...	2026-06-10 10:26:22.982312
23	Divulgación	3	Modificar	borrador	Aileen Moyeja	Actualizado el borrador de la publicación ID: 3	2026-06-10 10:27:07.434817
24	Divulgación	3	Modificar	publicado	Director	Aprobada y publicada en la Web institucional: Taller de Crisis Climática en Quíbor...	2026-06-10 19:10:08.515401
25	Divulgación	4	Crear	borrador	Mariangel Reyes	Creado contenido informativo: Bobare...	2026-06-10 19:52:35.64167
26	Divulgación	4	Eliminar	\N	Mariangel Reyes	Eliminado borrador permanentemente: Bobare...	2026-06-10 20:07:46.147818
27	Divulgación	5	Crear	borrador	Mariangel Reyes	Creado contenido informativo: Bobare...	2026-06-10 20:08:01.509544
28	Divulgación	6	Crear	borrador	Angel Ferrer	Creado contenido informativo: Finlandia...	2026-06-10 20:12:45.050829
29	Divulgación	7	Crear	borrador	Mariangel Reyes	Creado contenido informativo: 22...	2026-06-10 20:37:17.341712
30	Divulgación	7	Eliminar	\N	Gabriel Castañeda	Eliminado borrador permanentemente: 22...	2026-06-10 20:54:58.892448
31	Divulgación	5	Modificar	publicado	Gabriel Castañeda	Aprobada y publicada en la Web institucional: Bobare...	2026-06-10 21:05:52.641039
32	Divulgación	5	Modificar	borrador	Aileen Moyeja	Retirada de la web (Devuelta a borrador): Bobare...	2026-06-10 21:14:54.551101
33	Divulgación	5	Modificar	publicado	Aileen Moyeja	Actualizado ID: 5	2026-06-10 21:20:06.006219
34	Divulgación	6	Eliminar	\N	Aileen Moyeja	Eliminado permanentemente: Finlandia...	2026-06-10 21:20:15.391376
35	Usuarios	1	Modificar	Administrador	Alcides Romero	Editado usuario director@oncc.com	2026-06-17 11:07:43.24596
36	Usuarios	2	Crear	Administrador	Alcides Romero	Creado usuario maruchan@gmail.com	2026-06-17 11:14:57.864447
37	Usuarios	1	Modificar	Administrador	Director Regional	Editado usuario director@oncc.com	2026-06-17 11:18:09.126253
38	Usuarios	3	Crear	Administrador	Director Regional	Creado usuario a@gmail.com	2026-06-17 11:18:35.411456
39	Usuarios	3	Eliminar	\N	Director Regional	Eliminado usuario a@gmail.com	2026-06-17 11:18:42.621297
40	Usuarios	4	Crear	Administrador	Mariangel Reyes	Creado usuario moyejada@gmail.com	2026-06-17 12:41:46.50531
41	inventario	1	creacion	En Uso (Asignado)	Mariangel Reyes	Registro del equipo EMA-055	2026-06-17 12:43:28.62243
42	inventario	1	modificacion	En Uso (Asignado)	Mariangel Reyes	Datos del equipo EMA-055 actualizados	2026-06-17 12:43:48.556601
43	Usuarios	2	Modificar	Tecnico	Mariangel Reyes	Editado usuario maruchan@gmail.com	2026-06-17 13:17:31.779376
44	Usuarios	5	Crear	Administrador	Aileen Moyeja	Creado usuario gabrilucho@gmail.com	2026-06-17 13:38:50.017072
45	Usuarios	6	Crear	Tecnico	Aileen Moyeja	Creado usuario ferrari@gmai.com	2026-06-17 13:39:27.883761
\.


--
-- Data for Name: comunidad; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.comunidad (id_comunidad, id_parroquia, nombre_comunidad) FROM stdin;
1	1	Comunidad General
\.


--
-- Data for Name: divulgacion; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.divulgacion (id_divulgacion, id_actividad, nombre_divulgacion, descripcion_divulgacion, permiso_divulgacion) FROM stdin;
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

COPY public.formacion (id_formacion, nombre_formacion, id_actividad, id_institucion) FROM stdin;
\.


--
-- Data for Name: institucion; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.institucion (id_institucion, id_comunidad, nombre_institucion, tipo_institucion, direccion_exacta, numero_contacto, correo_electronico) FROM stdin;
34	1	Institución General	Comunitaria	Sin dirección registrada	Sin contacto	sin-correo@oncc.local
\.


--
-- Data for Name: inventario_equipos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.inventario_equipos (id, tipo_equipo, codigo, ubicacion, estado_operativo, estado_flujo, ultimo_mantenimiento, responsable, creado_en, actualizado_en, numero_serie, marca, modelo, observaciones, id_usuario) FROM stdin;
1	Estación Meteorológica (EMA)	EMA-055	Carabobo	Requiere Mantenimiento	En Uso (Asignado)	2026-01-01	Aileen Moyeja	2026-06-17 12:43:28.609551	2026-06-17 12:43:48.556601	\N	\N	\N	\N	\N
\.


--
-- Data for Name: mapas_registro; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mapas_registro (id, nombre, tipo_mapa, archivo, estado, version, cobertura, responsable, creado_en, actualizado_en, id_parroquia) FROM stdin;
\.


--
-- Data for Name: modulos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.modulos (id_modulo, nombre_modulo, descripcion_modulo) FROM stdin;
1	manage_users	Crear/Editar/Eliminar usuarios
2	manage_roles	Gestionar roles y permisos
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

COPY public.nivel (id_nivel, nombre_nivel, "descripción ") FROM stdin;
41	Base	Nivel base para registros iniciales
\.


--
-- Data for Name: parroquia; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.parroquia (id_parroquia, id_municipio, nombre_parroquia) FROM stdin;
1	1	Catedral
\.


--
-- Data for Name: publicaciones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.publicaciones (id, tipo, titulo, resumen, contenido, estado, publicado_en, creado_en, actualizado_en, id_usuario, id_divulgacion, prioridad) FROM stdin;
5	informe	Estado del Clima Global 2026: Aceleración del Calentamiento y Eventos Extremos	El presente informe ofrece un análisis exhaustivo de los indicadores climáticos globales correspondientes al primer semestre de 2026. Se destaca un incremento sin precedentes en las anomalías de temperatura de la superficie del mar, una pérdida acelerada de masa boral y un aumento drástico en la frecuencia de fenómenos meteorológicos extremos en latitudes medias. El documento insta a la revisión urgente de las metas de descarbonización para evitar puntos de no retorno del sistema climático.	El año 2026 ha comenzado registrando hitos climáticos alarmantes que desafían las proyecciones más conservadoras de los modelos meteorológicos. A continuación, se detallan los tres ejes principales de observación y preocupación científica: 1. Anomalías Térmicas y OcéanosLos océanos del planeta han absorbido más del 90% del exceso de calor atrapado por los gases de efecto invernadero. Durante los últimos seis meses, la temperatura media de la superficie del mar ha superado en el promedio histórico del periodo 1991-2020. Esto ha desencadenado eventos de blanqueamiento masivo de corales en el Pacífico y ha alterado las corrientes marinas que regulan el clima de Europa y América del Norte. 2. Desglaciación y Nivel del Mar La tasa de fusión en las capas de hielo de Groenlandia y la Antártida Occidental ha mostrado un incremento del 15% en comparación con el año anterior. El agua de deshielo continental, sumada a la expansión térmica del agua marina, ha elevado el nivel medio del mar a una velocidad. 3. Fenómenos Meteorológicos Extremos La atmósfera, al estar más caliente, retiene mayor humedad (aproximadamente un 7% más por cada grado Celsius de calentamiento). Esto ha provocado una preocupante dualidad climática: Precipitaciones torrenciales e inundaciones récord en regiones monzónicas y zonas costeras de Asia. Sequías prolongadas y olas de calor persistentes en el sur de Europa y el cono sur de América, intensificando la temporada de incendios forestales. Conclusión del Panel de Expertos: "Los datos de 2026 no son una simple desviación estadística; son el reflejo de un sistema climático que busca un nuevo equilibrio, uno mucho más hostil para la infraestructura y la vida humana tal como la conocemos."	publicado	\N	2026-06-10 20:08:01.473563	2026-06-10 21:20:05.982824	7	\N	1
\.


--
-- Data for Name: reportes_transaccionales; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reportes_transaccionales (id, titulo, modulo_origen, rango_desde, rango_hasta, formato, estado, responsable, creado_en, actualizado_en) FROM stdin;
\.


--
-- Data for Name: sensibilizacion; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sensibilizacion (id_sensivilizacion, nombre_sensivilizacion, id_actividad) FROM stdin;
\.


--
-- Data for Name: tecnicos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tecnicos (id_tecnico, cedula, nombres, apellidos, id_usuario) FROM stdin;
\.


--
-- Data for Name: temas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.temas (id_tema, nombre_tema, descripcion_tema) FROM stdin;
\.


--
-- Data for Name: usuario; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuario (id_usuario, nombre_usuario, "clave usuario") FROM stdin;
1	Director	scrypt:32768:8:1$iPvDHWVySiWslJCE$d11ab552a937859fb34e8743fc7086d8b692801a465a8c17dd2a7664e8aa1ed255b47d7062271c8d9bc7039ca95f146b79bf7ef2329720d6cfa0cce42a95b8c6
7	Mariangel Reyes	scrypt:32768:8:1$pqk91tK6ynyN1UE3$b977150f12639f60961e6d9bcb85b9d457b2339e30a8c9a5ce3bb4df55310bc75965fa09a956ec99c1637ff0fb9e55fbb826362045fdf3c5e53d022022e8f706
8	Aileen Moyeja	scrypt:32768:8:1$6WH5iJGAJvHfNmTZ$b58a41261ce490977c230b27ed35f90bef8962270da9f4bc9002186d7915b9f466bdee8dcfae1fd494fa156c45339bf95440f8fbaa18852dd30566981b359a49
9	Angel Ferrer	scrypt:32768:8:1$glkpKU3D5avbfljY$39d935a4e548391ed61dfcd9b6d0b1b026e9b404cbdc613df4520e44c65f81992fde6bf608621aa566632e510efcffe3bcdf0a53d1157c175052a6c7a2cd26b8
10	Gabriel Castañeda	scrypt:32768:8:1$O3feRPG6fm3DIcDX$87d4665da39ced29921e887a79b16b2cb9c40e2e99aa6d16fb7d8dd25417597af00738bdb1799c0bfef0075a5c7c34a240ad6c76012726ea8e5f9968f6ea3ade
\.


--
-- Data for Name: visitas_portal; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.visitas_portal (id, mes, creado_en) FROM stdin;
1	2026-06	2026-06-07 22:20:07.775002
2	2026-06	2026-06-09 00:00:57.921269
3	2026-06	2026-06-10 03:05:30.337987
4	2026-06	2026-06-10 03:05:32.802172
5	2026-06	2026-06-10 10:05:00.336891
6	2026-06	2026-06-10 18:31:25.747203
7	2026-06	2026-06-17 09:35:34.035413
8	2026-06	2026-06-17 12:28:06.337253
9	2026-06	2026-06-17 13:36:46.674893
10	2026-06	2026-06-17 21:53:00.210292
11	2026-06	2026-06-17 22:06:46.142903
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
-- Name: bitacora_transacciones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bitacora_transacciones_id_seq', 45, true);


--
-- Name: comunidad_id_comunidad_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.comunidad_id_comunidad_seq', 36, true);


--
-- Name: divulgacion_id_divulgacion_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.divulgacion_id_divulgacion_seq', 1, false);


--
-- Name: estado_id_estado_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.estado_id_estado_seq', 36, true);


--
-- Name: formacion_id_formacion_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.formacion_id_formacion_seq', 1, false);


--
-- Name: intitucion_id_institucion_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.intitucion_id_institucion_seq', 34, true);


--
-- Name: inventario_equipos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.inventario_equipos_id_seq', 1, true);


--
-- Name: mapas_registro_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.mapas_registro_id_seq', 1, false);


--
-- Name: modulos_id_modulo_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.modulos_id_modulo_seq', 2, true);


--
-- Name: municipio_id_municipio_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.municipio_id_municipio_seq', 36, true);


--
-- Name: nivel_id_nivel_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.nivel_id_nivel_seq', 41, true);


--
-- Name: parroquia_id_parroquia_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.parroquia_id_parroquia_seq', 36, true);


--
-- Name: publicaciones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.publicaciones_id_seq', 7, true);


--
-- Name: reportes_transaccionales_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reportes_transaccionales_id_seq', 1, false);


--
-- Name: sensibilizacion _id_sensivilizacion_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public."sensibilizacion _id_sensivilizacion_seq"', 1, false);


--
-- Name: tecnicos_id_tecnico_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tecnicos_id_tecnico_seq', 1, false);


--
-- Name: temas_id_tema_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.temas_id_tema_seq', 1, false);


--
-- Name: usuario_id_usuario_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usuario_id_usuario_seq', 10, true);


--
-- Name: visitas_portal_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.visitas_portal_id_seq', 11, true);


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
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: bitacora_transacciones bitacora_transacciones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bitacora_transacciones
    ADD CONSTRAINT bitacora_transacciones_pkey PRIMARY KEY (id);


--
-- Name: comunidad comunidad_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comunidad
    ADD CONSTRAINT comunidad_pkey PRIMARY KEY (id_comunidad);


--
-- Name: divulgacion divulgacion_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.divulgacion
    ADD CONSTRAINT divulgacion_pkey PRIMARY KEY (id_divulgacion);


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
-- Name: formacion formacion_id_actividad _key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.formacion
    ADD CONSTRAINT "formacion_id_actividad _key" UNIQUE (id_actividad);


--
-- Name: formacion formacion_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.formacion
    ADD CONSTRAINT formacion_pkey PRIMARY KEY (id_formacion);


--
-- Name: institucion intitucion_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.institucion
    ADD CONSTRAINT intitucion_pkey PRIMARY KEY (id_institucion);


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
-- Name: mapas_registro mapas_registro_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mapas_registro
    ADD CONSTRAINT mapas_registro_pkey PRIMARY KEY (id);


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
    ADD CONSTRAINT publicaciones_pkey PRIMARY KEY (id);


--
-- Name: reportes_transaccionales reportes_transaccionales_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reportes_transaccionales
    ADD CONSTRAINT reportes_transaccionales_pkey PRIMARY KEY (id);


--
-- Name: sensibilizacion sensibilizacion _id_actividad_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sensibilizacion
    ADD CONSTRAINT "sensibilizacion _id_actividad_key" UNIQUE (id_actividad);


--
-- Name: sensibilizacion sensibilizacion _pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sensibilizacion
    ADD CONSTRAINT "sensibilizacion _pkey" PRIMARY KEY (id_sensivilizacion);


--
-- Name: tecnicos tecnicos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tecnicos
    ADD CONSTRAINT tecnicos_pkey PRIMARY KEY (id_tecnico);


--
-- Name: temas temas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.temas
    ADD CONSTRAINT temas_pkey PRIMARY KEY (id_tema);


--
-- Name: tecnicos uq_cedula_tecnico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tecnicos
    ADD CONSTRAINT uq_cedula_tecnico UNIQUE (cedula);


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
-- Name: ix_visitas_portal_mes; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_visitas_portal_mes ON public.visitas_portal USING btree (mes);


--
-- Name: actividad_tecnico activ_tecn_id_actividad_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.actividad_tecnico
    ADD CONSTRAINT activ_tecn_id_actividad_fkey FOREIGN KEY (id_actividad) REFERENCES public.actividad(id_actividad) ON DELETE CASCADE;


--
-- Name: actividad_tecnico activ_tecn_id_tecnico_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.actividad_tecnico
    ADD CONSTRAINT activ_tecn_id_tecnico_fkey FOREIGN KEY (id_tecnico) REFERENCES public.tecnicos(id_tecnico) ON DELETE CASCADE;


--
-- Name: actividad actividad_id_comunidad_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.actividad
    ADD CONSTRAINT actividad_id_comunidad_fkey FOREIGN KEY (id_comunidad) REFERENCES public.comunidad(id_comunidad);


--
-- Name: actividad actividad_id_nivel_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.actividad
    ADD CONSTRAINT actividad_id_nivel_fkey FOREIGN KEY (id_nivel) REFERENCES public.nivel(id_nivel);


--
-- Name: comunidad comunidad_id_parroquia_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comunidad
    ADD CONSTRAINT comunidad_id_parroquia_fkey FOREIGN KEY (id_parroquia) REFERENCES public.parroquia(id_parroquia);


--
-- Name: actividad fk_actividad_usuario; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.actividad
    ADD CONSTRAINT fk_actividad_usuario FOREIGN KEY (id_usuario) REFERENCES public.usuario(id_usuario) ON DELETE SET NULL;


--
-- Name: divulgacion fk_divulgacion_actividad; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.divulgacion
    ADD CONSTRAINT fk_divulgacion_actividad FOREIGN KEY (id_actividad) REFERENCES public.actividad(id_actividad) ON DELETE CASCADE;


--
-- Name: formacion fk_formacion_actividad; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.formacion
    ADD CONSTRAINT fk_formacion_actividad FOREIGN KEY (id_actividad) REFERENCES public.actividad(id_actividad) ON DELETE CASCADE;


--
-- Name: institucion fk_institucion_comunidad; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.institucion
    ADD CONSTRAINT fk_institucion_comunidad FOREIGN KEY (id_comunidad) REFERENCES public.comunidad(id_comunidad) ON DELETE CASCADE;


--
-- Name: inventario_equipos fk_inventario_usuario; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventario_equipos
    ADD CONSTRAINT fk_inventario_usuario FOREIGN KEY (id_usuario) REFERENCES public.usuario(id_usuario) ON DELETE SET NULL;


--
-- Name: mapas_registro fk_mapas_parroquia; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mapas_registro
    ADD CONSTRAINT fk_mapas_parroquia FOREIGN KEY (id_parroquia) REFERENCES public.parroquia(id_parroquia) ON DELETE SET NULL;


--
-- Name: publicaciones fk_publicaciones_divulgacion; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.publicaciones
    ADD CONSTRAINT fk_publicaciones_divulgacion FOREIGN KEY (id_divulgacion) REFERENCES public.divulgacion(id_divulgacion) ON DELETE CASCADE;


--
-- Name: publicaciones fk_publicaciones_usuario; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.publicaciones
    ADD CONSTRAINT fk_publicaciones_usuario FOREIGN KEY (id_usuario) REFERENCES public.usuario(id_usuario) ON DELETE CASCADE;


--
-- Name: sensibilizacion fk_sensibilizacion_actividad; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sensibilizacion
    ADD CONSTRAINT fk_sensibilizacion_actividad FOREIGN KEY (id_actividad) REFERENCES public.actividad(id_actividad) ON DELETE CASCADE;


--
-- Name: actividad_tecnico fk_tecnico_intermedia; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.actividad_tecnico
    ADD CONSTRAINT fk_tecnico_intermedia FOREIGN KEY (id_tecnico) REFERENCES public.tecnicos(id_tecnico) ON DELETE CASCADE;


--
-- Name: tecnicos fk_tecnicos_usuario; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tecnicos
    ADD CONSTRAINT fk_tecnicos_usuario FOREIGN KEY (id_usuario) REFERENCES public.usuario(id_usuario) ON DELETE SET NULL;


--
-- Name: formacion formacion_id_institucion_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.formacion
    ADD CONSTRAINT formacion_id_institucion_fkey FOREIGN KEY (id_institucion) REFERENCES public.institucion(id_institucion);


--
-- Name: municipio municipio_id_estado_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.municipio
    ADD CONSTRAINT municipio_id_estado_fkey FOREIGN KEY (id_estado) REFERENCES public.estado(id_estado);


--
-- Name: parroquia parroquia_id_municipio_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parroquia
    ADD CONSTRAINT parroquia_id_municipio_fkey FOREIGN KEY (id_municipio) REFERENCES public.municipio(id_municipio);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;


--
-- PostgreSQL database dump complete
--

\unrestrict egLdFXOyq8F9tUp5pBRDMftm2fkLkJqGghTLH7UMUMhfB3QSNRMm1fyPu1OK86u

