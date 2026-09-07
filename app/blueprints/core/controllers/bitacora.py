from flask import render_template, request
from flask_login import login_required
from app.blueprints.core import core_bp
from app.blueprints.core.controllers.roles import verificar_permiso_dinamico
from app.models.bitacora import BitacoraTransaccion


@core_bp.route('/bitacora')
@login_required
def bitacora_index():
    verificar_permiso_dinamico('gestionar_usuarios')

    pagina = request.args.get('page', 1, type=int)
    modulo_filtro = request.args.get('modulo', '').strip()

    query = BitacoraTransaccion.query
    if modulo_filtro:
        query = query.filter(BitacoraTransaccion.modulo.ilike(f"%{modulo_filtro}%"))

    # Paginamos a 15 registros por página
    paginacion = query.order_by(BitacoraTransaccion.id.desc()).paginate(
        page=pagina, 
        per_page=15, 
        error_out=False
    )

    return render_template(
        'parametrizacion/bitacora.html',
        paginacion=paginacion,
        registros=paginacion.items,
        modulo_actual=modulo_filtro
    )