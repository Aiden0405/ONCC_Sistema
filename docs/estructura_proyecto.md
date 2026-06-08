# Estructura del proyecto ONCC

Este documento toma como fuente de verdad el export SQL del ERD entregado para revisión, que ahora vive en [database/sql.sql](database/sql.sql).
El archivo [archive/20260607/oncc_schema.sql](archive/20260607/oncc_schema.sql) conserva la versión histórica del esquema para referencia, pero ya no forma parte de la base activa.

## Vista / UI

Todo lo visible para el usuario vive en `app/templates/` y `app/static/`.

- `app/templates/base.html`: layout principal del sistema interno.
- `app/templates/public/`: portal público.
- `app/templates/divulgacion/`: panel administrativo de publicaciones.
- `app/templates/usuarios/`, `app/templates/roles/`, `app/templates/actividades/`, `app/templates/geomatica/`, etc.: vistas por dominio.
- `app/static/`: CSS, JS, imágenes y archivos subidos.

## Backend

La lógica de negocio vive en `app/blueprints/`, `app/models/`, `app/services/`, `app/utils/` y `app/cli.py`.

### Ubicación recomendada de archivos

- `database/sql.sql`: esquema activo del proyecto.
- `app/models/`: modelos ORM alineados con el esquema activo.
- `app/blueprints/`: rutas y controladores por dominio.
- `app/services/`: procesos reutilizables como sesión, notificación y auditoría.
- `app/utils/`: utilidades comunes y decoradores.
- `app/templates/`: HTML por módulo.
- `app/static/`: CSS, JavaScript, imágenes y subidas.
- `migrations/`: migraciones versionadas de la base de datos.
- `archive/`: archivos antiguos o congelados que ya no deben usarse como fuente activa.

### Servicios clave

- `app/services/gestor_sesion.py`: encapsula el inicio y cierre de sesión con Flask-Login y la recuperación de contraseña.
- `app/services/notificacion.py`: servicio de salida para publicar o disparar integraciones externas cuando una publicación pasa a estado publicado.

### Dominios principales según la base de datos entregada

- `core`: `usuario`, `roles`, `permiso`, `modulos`.
- `territorio`: `estado`, `municipio`, `parroquia`, `comunidad`, `ubicacion `.
- `comunitario`: `actividad`, `nivel`, `formacion`, `sensibilizacion `, `material`, `intitucion`.
- `monitoreo`: `monitoreo`, `actividad_tecnico`, `pruebas`, `imagenes_pruebas`.
- `mapas`: `mapa_riesgo`, `mapa_climatico`, `imagenes_publicacion`.
- `logistica`: `tecnicos`, `modelo`, `modelos_equipo`, `equipo`, `ubicacion_equipo`, `movimientos`, `equipo_monitoreo`.
- `divulgacion`: `divulgacion`, `publicacion`, `imagenes`.

### Mapa módulo a tabla

- `core`: autenticación, usuarios, roles y permisos.
- `comunitario`: actividades comunitarias, formaciones y sensibilizaciones.
- `monitoreo`: actividad-tecnico, monitoreo y pruebas.
- `mapas`: mapas de riesgo y mapas climáticos.
- `logistica`: técnicos, modelos, equipos y movimientos.
- `divulgacion`: divulgación, publicaciones e imágenes.

### Correspondencia técnica actual

- `app.models.usuario` -> `usuario`
- `app.models.role` -> `roles` y `modulos`
- `app.models.divulgacion` -> `publicaciones` de compatibilidad
- `app.models.actividad` -> `actividades` de compatibilidad
- `app.models.geomatica` -> `mapas_registro` de compatibilidad
- `app.models.inventario` -> `inventario_equipos` de compatibilidad
- `app.models.reporte` -> `reportes_transaccionales` de compatibilidad
- `app.models.visita_portal` -> `visitas_portal` de compatibilidad
- `app.models.password_reset` -> `password_resets` de compatibilidad

### Módulo de divulgación

- Panel interno: lista publicaciones, crea borradores y aprueba contenidos.
- Portal público: muestra solo publicaciones con estado `publicado`.
- Flujo principal: borrador -> aprobado/publicado -> visible en portal.

## Esquema PostgreSQL entregado

El archivo [archive/20260607/oncc_schema.sql](archive/20260607/oncc_schema.sql) queda solo como referencia histórica/legado.

### Núcleo territorial

- `estado`
- `municipio`
- `parroquia`
- `comunidad`
- `ubicacion `

Relaciones principales:

- `municipio.id_estado -> estado.id_estado`
- `parroquia.id_municipio -> municipio.id_municipio`
- `comunidad.id_parroquia -> parroquia.id_parroquia`
- `ubicacion .id_parroquia -> parroquia.id_parroquia`

### Seguridad y acceso

- `usuario`
- `roles`
- `permiso`
- `modulos`

Relaciones principales:

- `usuario.id_rol -> roles.id_rol`
- `permiso.id_rol -> roles.id_rol`
- `permiso.id_modulo -> modulos.id_modulo`

### Auditoría y portal

- `divulgacion`
- `publicacion`
- `imagenes`

### Comunitario

- `actividad`
- `nivel`
- `formacion`
- `sensibilizacion `
- `material`
- `intitucion`

Relaciones principales:

- `actividad.id_comunidad -> comunidad.id_comunidad`
- `actividad.id_nivel -> nivel.id_nivel`
- `formacion.id_actividad -> actividad.id_actividad`
- `formacion.id_institucion -> intitucion.id_institucion`
- `sensibilizacion .id_actividad -> actividad.id_actividad`
- `material.id_nivel -> nivel.id_nivel`
- `intitucion.id_comunidad -> comunidad.id_comunidad`

### Monitoreo y operación

- `tecnicos`
- `monitoreo`
- `actividad_tecnico`
- `pruebas`
- `imagenes_pruebas`

Relaciones principales:

- `actividad_tecnico.id_actividad -> actividad.id_actividad`
- `actividad_tecnico.id_tecnico -> tecnicos.id_tecnicos`
- `monitoreo.id_actividad -> actividad.id_actividad`
- `pruebas.id_actividad -> actividad.id_actividad`
- `imagenes_pruebas.id_pruebas -> pruebas.id_pruebas`

### Geomática

- `mapa_riesgo`
- `mapa_climatico`

Relaciones principales:

- `mapa_riesgo.id_comunidad -> comunidad.id_comunidad`
- `mapa_riesgo.id_sensibilizacion -> sensibilizacion .id_sensivilizacion`
- `mapa_climatico.id_parroquia -> parroquia.id_parroquia`

### Logística

- `modelo`
- `modelos_equipo`
- `equipo`
- `ubicacion_equipo`
- `movimientos`

## Modelos actuales y compatibilidad

Los modelos activos del sistema están en `app/models/`.

- `usuario.py`
- `role.py`
- `bitacora.py`
- `divulgacion.py`
- `actividad.py`
- `inventario.py`
- `reporte.py`
- `visita_portal.py`
- `password_reset.py`
- `geomatica.py`

El punto de compatibilidad más sensible sigue siendo geomática, porque el código existente todavía usa nombres previos mientras la base entregada trabaja con `mapa_riesgo` y `mapa_climatico`.

## Formularios core

- `app/blueprints/core/forms.py`: validaciones de login, recuperación y publicaciones.

## Arranque

- `run.py` crea la app.
- `app/__init__.py` registra extensiones, blueprints y rutas de compatibilidad.
- `init_db.py` ejecuta el seed inicial.

## Base de datos

El sistema ya está preparado para PostgreSQL desde `config.py`.
Para trabajar con la base entregada, la variable `DB_ENGINE` debe apuntar a `postgresql` o definirse `DATABASE_URL` con la cadena completa.
SQLite queda solo como respaldo local para desarrollo rápido.

Flujo recomendado:

- instalar PostgreSQL
- crear la base `oncc_sistema`
- ejecutar `database/sql.sql`
- actualizar `.env` con `DATABASE_URL` o `DB_ENGINE=postgresql`
- correr `flask db upgrade` si las migraciones quedan alineadas

## Nota práctica

La separación real es esta:

- Vista/UI: plantillas, estilos, JavaScript e imágenes.
- Backend: blueprints, modelos, servicios, utilidades y migraciones.

Si un archivo solo define HTML/CSS/JS, es vista/UI.
Si un archivo define rutas, consultas, validaciones o reglas de negocio, es backend.

### Estructura recomendada actual

- `app/blueprints/`: organización por dominio funcional.
- `app/models/`: entidades persistentes.
- `app/services/`: lógica de negocio y procesos reutilizables.
- `app/utils/`: decoradores y utilidades comunes.
- `app/templates/`: vistas por módulo.
- `app/static/`: recursos estáticos.
- `migrations/`: cambios de esquema versionados.
- `tests/`: pruebas automatizadas.