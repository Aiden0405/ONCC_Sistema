# Estructura del proyecto ONCC

## Vista / UI

Todo lo visible para el usuario vive en `app/templates/` y `app/static/`.

- `app/templates/base.html`: layout principal del sistema interno.
- `app/templates/public/`: portal público.
- `app/templates/divulgacion/`: panel administrativo de publicaciones.
- `app/templates/usuarios/`, `app/templates/roles/`, `app/templates/actividades/`, etc.: vistas por dominio.
- `app/static/`: CSS, JS, imágenes y archivos subidos.

## Backend

La lógica de negocio vive en `app/blueprints/`, `app/models/`, `app/services/`, `app/utils/` y `app/cli.py`.

### Servicios clave

- `app/services/gestor_sesion.py`: encapsula el inicio y cierre de sesión con Flask-Login y la recuperación de contraseña.
- `app/services/notificacion.py`: servicio de salida para publicar o disparar integraciones externas cuando una publicación pasa a estado publicado.

### Dominios principales

- `core`: usuarios, autenticación, roles, bitácora y divulgación.
- `comunitario`: formaciones y sensibilizaciones.
- `mapas`: mapas de riesgo y mapas climáticos.
- `monitoreo`: tabla de actividades y comparación de mapas climáticos.
- `logistica`: técnicos de campo e inventario de equipos.

### Módulo de divulgación

- Panel interno: lista publicaciones, crea borradores y aprueba contenidos.
- Portal público: muestra solo publicaciones con estado `publicado`.
- Flujo principal: borrador -> aprobado/publicado -> visible en portal.

## Modelos actuales

Los modelos activos del sistema están en `app/models/`:

- `usuario.py`
- `role.py`
- `bitacora.py`
- `divulgacion.py`
- `actividad.py`
- `geomatica.py`
- `inventario.py`
- `reporte.py`
- `visita_portal.py`
- `password_reset.py`

El modelo `password_reset.py` guarda tokens temporales para recuperación de contraseña.

## Formularios core

- `app/blueprints/core/forms.py`: validaciones de login, recuperación y publicaciones.

## Base de datos

- `database/oncc_schema.sql`: esquema PostgreSQL limpio alineado con el sistema actual.
- `migrations/`: migraciones de Alembic para evolución del esquema.

Tablas importantes ya reflejadas en el esquema:

- `usuarios` usa `correo` como columna de login.
- `publicaciones` guarda el contenido editorial que alimenta el portal público.

## Arranque

- `run.py` crea la app.
- `app/__init__.py` registra extensiones, blueprints y rutas de compatibilidad.
- `init_db.py` ejecuta el seed inicial.

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