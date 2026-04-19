# ONCC Sistema - Guia de Arquitectura

## 1) Modulos transaccionales principales

1. Inventario
2. Mapas (Geomatica)
3. Reportes
4. Formaciones
5. Sensibilizaciones

Estos 5 modulos son el nucleo funcional del sistema y deben conservar el flujo:

- borrador
- en_revision
- aprobado
- cerrado

La lista oficial de estados esta centralizada en app/constants.py.

Nomenclatura operativa aplicada en el sistema:

- "Divulgacion" es el nombre funcional del modulo de sensibilizaciones.
- "Monitoreo General" es el tablero integrado (ruta /monitoreo) y no duplica datos de Geomatica.

## 2) Modulos de soporte

- Comunidades: flujo de campo para expedientes de mapa de riesgo.
- Actividades: registro operativo de jornadas y evidencias.
- Entes/Solicitudes: integracion institucional.
- Auth/Usuarios: acceso y seguridad.
- Bitacora: trazabilidad de acciones.

Estos modulos soportan el proceso, pero no reemplazan ni duplican los 5 transaccionales.

## 3) Estructura tecnica

- app/models: entidades SQLAlchemy
- app/controllers: rutas y logica de negocio por modulo
- app/templates: vistas HTML por modulo
- app/services: servicios auxiliares (PDF, procesamiento SSBC)
- app/constants.py: reglas compartidas (estados/fases)

## 4) Regla de consistencia

Toda accion relevante debe registrar bitacora:

- modulo
- registro_id
- accion
- estado_nuevo
- usuario
- detalle

## 5) Configuracion de base de datos

Se admite SQLite, PostgreSQL y MySQL desde variables de entorno (config.py):

- DATABASE_URL (prioridad alta)
- o DB_ENGINE + DB_HOST + DB_PORT + DB_NAME + DB_USER + DB_PASSWORD

Para ejemplos de entorno usar .env.example.

## 6) Siguiente paso recomendado

Implementar migraciones con Flask-Migrate/Alembic para evitar depender de db.create_all() en ambientes productivos.
