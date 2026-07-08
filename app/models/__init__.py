# === SUBIMOS LA SEGURIDAD AL PRINCIPIO PARA EVITAR QUE FALLE LA TABLA INTERMEDIA ===
from app.models.role import Role
from app.models.usuario import Usuario

# === EL RESTO DE TUS MODELOS TRANSACCIONALES ===
from app.models.actividad import Actividad
from app.models.bitacora import BitacoraTransaccion
from app.models.divulgacion import Publicacion
from app.models.geomatica import MapaRiesgo
from app.models.inventario import InventarioEquipo
from app.models.esquema_activo import ActividadActiva
from app.models.esquema_activo import ComunidadActiva
from app.models.esquema_activo import EstadoActivo
from app.models.esquema_activo import FormacionActiva
from app.models.esquema_activo import InstitucionActiva
from app.models.esquema_activo import NivelActivo
from app.models.esquema_activo import MunicipioActivo
from app.models.esquema_activo import ParroquiaActiva
from app.models.esquema_activo import SensibilizacionActiva
from app.models.reporte import ReporteTransaccional