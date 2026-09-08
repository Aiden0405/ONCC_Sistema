ESTADOS_TRANSACCION = ['borrador', 'en_revision', 'aprobado', 'cerrado']

ESTADOS_ACTIVIDAD = ['Planificada', 'En proceso', 'Completado', 'Suspendida']

FASES_COMUNIDAD_MAPA = [
    'Diagnóstico / Acercamiento',
    'Recolección de Datos',
    'Elaboración e Impresión',
    'Entrega del Mapa',
]

# Slugs funcionales permitidos en el catalogo global de permisos.
# Los permisos legacy se conservan en el seed solo para compatibilidad.
KNOWN_PERMISSION_SLUGS = (
    'ver_usuarios', 'registrar_usuarios', 'editar_usuarios', 'eliminar_usuarios',
    'ver_roles', 'registrar_roles', 'editar_roles', 'eliminar_roles',
    'asignar_permisos_roles', 'ver_permisos', 'registrar_permisos',
    'editar_permisos', 'eliminar_permisos', 'ver_bitacora', 'ver_catalogos',
    'ver_actividades', 'registrar_actividades', 'editar_actividades',
    'eliminar_actividades', 'cambiar_estado_actividades',
    'ver_formaciones', 'registrar_formaciones', 'editar_formaciones',
    'eliminar_formaciones', 'cambiar_estado_formaciones',
    'ver_sensibilizaciones', 'registrar_sensibilizaciones',
    'editar_sensibilizaciones', 'eliminar_sensibilizaciones',
    'cambiar_estado_sensibilizaciones',
    'ver_divulgaciones', 'registrar_divulgaciones', 'editar_divulgaciones',
    'eliminar_divulgaciones', 'aprobar_divulgaciones', 'publicar_divulgaciones',
    'despublicar_divulgaciones',
    'ver_instituciones', 'registrar_instituciones', 'editar_instituciones',
    'eliminar_instituciones', 'ver_comunidades', 'registrar_comunidades',
    'editar_comunidades', 'eliminar_comunidades', 'ver_niveles',
    'registrar_niveles', 'editar_niveles', 'eliminar_niveles',
    'ver_mapas_riesgo', 'registrar_mapas_riesgo', 'editar_mapas_riesgo',
    'eliminar_mapas_riesgo', 'ver_elementos_mapa', 'registrar_elementos_mapa',
    'editar_elementos_mapa', 'eliminar_elementos_mapa', 'ver_simbologia',
    'registrar_simbologia', 'editar_simbologia', 'eliminar_simbologia',
    'ver_mapas_climaticos', 'registrar_mapas_climaticos',
    'editar_mapas_climaticos', 'eliminar_mapas_climaticos',
    'ver_inventario', 'registrar_inventario', 'editar_inventario',
    'eliminar_inventario', 'ver_movimientos_inventario',
    'registrar_movimientos_inventario', 'editar_movimientos_inventario',
    'eliminar_movimientos_inventario', 'ver_reportes_inventario',
    'ver_actas_inventario', 'ver_tecnicos', 'registrar_tecnicos',
    'editar_tecnicos', 'eliminar_tecnicos', 'ver_movimientos_tecnicos',
    'ver_reportes_tecnicos', 'consultar_geografia',
)
