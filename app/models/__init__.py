# Priorizamos los modelos del esquema activo para evitar conflictos con el esquema legado
from app.models.esquema_activo import (
    FormacionActiva,
    InstitucionActiva,
    NivelActivo,
    ActividadActiva,
    ComunidadActiva,
    EstadoActivo,
    MunicipioActivo,
    ParroquiaActiva,
    SensibilizacionActiva,
    Actividad as ActividadActivaAlias,
    Institucion as InstitucionActivaAlias,
    Sensibilizacion as SensibilizacionActivaAlias
)

from app.models.bitacora import BitacoraTransaccion
from app.models.divulgacion import Publicacion
from app.models.geomatica import MapaRiesgo
from app.models.inventario import InventarioEquipo

from app.models.reporte import ReporteTransaccional
from app.models.usuario import Usuario
