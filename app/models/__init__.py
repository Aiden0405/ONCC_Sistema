# Priorizamos los modelos del esquema activo para evitar conflictos con el esquema legado
from app.models.esquema_activo import (
    InstitucionActiva,
    NivelActivo,
    ActividadActiva,
    ComunidadActiva,
    EstadoActivo,
    MunicipioActivo,
    ParroquiaActiva,
    SensibilizacionActiva
)
from app.models.formacion import FormacionActiva
from app.models.bitacora import BitacoraTransaccion
from app.models.divulgacion import Publicacion
from app.models.geomatica import MapaRegistro
from app.models.inventario import InventarioEquipo

from app.models.reporte import ReporteTransaccional
from app.models.usuario import Usuario
