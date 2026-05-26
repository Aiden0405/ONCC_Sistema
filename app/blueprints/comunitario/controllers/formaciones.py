from flask import flash, redirect, render_template, request, url_for

from app.blueprints.comunitario import comunitario_bp


@comunitario_bp.route('/formaciones')
def formaciones_index():
    return render_template('formaciones/index.html')


@comunitario_bp.route('/formaciones/nuevo', methods=['POST'])
def formacion_nuevo():
    flash('Módulo de formaciones pendiente de implementación.', 'info')
    return redirect(url_for('formacion.index'))


@comunitario_bp.route('/formaciones/<int:formacion_id>/estado', methods=['POST'])
def formacion_cambiar_estado(formacion_id):
    flash('Módulo de formaciones pendiente de implementación.', 'info')
    return redirect(url_for('formacion.index'))