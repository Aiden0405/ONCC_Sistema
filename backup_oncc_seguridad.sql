--
-- PostgreSQL database dump
--

\restrict IamS5K6NI0tax9K9yNdx06U5WboLvP98qHbwJBv1Of6Bg6gCPoO7gbyiKWqRYUo

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: auditoria; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auditoria (
);


ALTER TABLE public.auditoria OWNER TO postgres;

--
-- Name: backup; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.backup (
);


ALTER TABLE public.backup OWNER TO postgres;

--
-- Name: permisos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.permisos (
);


ALTER TABLE public.permisos OWNER TO postgres;

--
-- Name: rol; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rol (
    id_rol integer NOT NULL,
    nombre_rol character varying(80) NOT NULL
);


ALTER TABLE public.rol OWNER TO postgres;

--
-- Name: sesiones ; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."sesiones " (
);


ALTER TABLE public."sesiones " OWNER TO postgres;

--
-- Name: usuario; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuario (
    id_usuario integer NOT NULL,
    nombre_usuario character varying(30) NOT NULL,
    correo character varying(50) NOT NULL,
    clave character varying(250) NOT NULL,
    id_rol integer DEFAULT 1 NOT NULL,
    estatus boolean DEFAULT true NOT NULL
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
-- Name: usuario id_usuario; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario ALTER COLUMN id_usuario SET DEFAULT nextval('public.usuario_id_usuario_seq'::regclass);


--
-- Data for Name: auditoria; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auditoria  FROM stdin;
\.


--
-- Data for Name: backup; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.backup  FROM stdin;
\.


--
-- Data for Name: permisos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.permisos  FROM stdin;
\.


--
-- Data for Name: rol; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.rol (id_rol, nombre_rol) FROM stdin;
1	Superusuario
2	Administrador
3	Tecnico
\.


--
-- Data for Name: sesiones ; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."sesiones "  FROM stdin;
\.


--
-- Data for Name: usuario; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuario (id_usuario, nombre_usuario, correo, clave, id_rol, estatus) FROM stdin;
1	Director Regional	director@oncc.com	scrypt:32768:8:1$87jmkGxcDBBmX0wm$e2f851dba238394c0e9341d6fd2b5849c1c1bbc5468ffb01e4d7b85a8a0f6d1312f89256d3e554b200156f8bcfdfa46d6e4d783ccae08c5530b3acbeff47a06c	1	t
4	Aileen Moyeja	moyejada@gmail.com	scrypt:32768:8:1$gWzZ18QlcvRuH56c$0a7fe348ceafa52a0326fd19965ba51e22b36c541b562b7dd3031337e73c6f4e03d9d8b1a79600a329f4328c0d9e904da6609ddf7307f91fe48a436142c9614b	1	t
2	Mariangel Reyes	maruchan@gmail.com	scrypt:32768:8:1$dUzD64KmnHWQHxFJ$990ae5e50f714411534cd9b6b09a46d2c4329528f9c0f1f740c73b62ad0a4cf31aed48225dde644d0186386a250fc52a576494b196014e544d0eb25fe7b1ba6b	3	t
5	Gabriel Castaneda	gabrilucho@gmail.com	scrypt:32768:8:1$Uq0ne8CIh6hnPwDG$fff57d087028d0fc1ddfdbf97da69e7e1988a10a1f75afec178f2771bfcd3a5193c0ba251404ccab560ef0ad253dd16c4b945e48a6c7534cfefe3e33508e1dc0	2	t
6	Angel Ferrer	ferrari@gmai.com	scrypt:32768:8:1$phGcRoyNCk7gJBic$d913b62d15b95641502453909939d9866252401b276628cd328a5f1f746fcfc6e973c08d3f79fde566645c36ff2684641e7afd204f280405d71c185484e76744	3	t
\.


--
-- Name: usuario_id_usuario_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usuario_id_usuario_seq', 6, true);


--
-- Name: rol rol_nombre_rol_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rol
    ADD CONSTRAINT rol_nombre_rol_key UNIQUE (nombre_rol);


--
-- Name: rol rol_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rol
    ADD CONSTRAINT rol_pkey PRIMARY KEY (id_rol);


--
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (id_usuario);


--
-- PostgreSQL database dump complete
--

\unrestrict IamS5K6NI0tax9K9yNdx06U5WboLvP98qHbwJBv1Of6Bg6gCPoO7gbyiKWqRYUo

