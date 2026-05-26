from flask import flash, redirect, render_template, url_for

from app.blueprints.comunitario import comunitario_bp


@comunitario_bp.route('/sensibilizaciones')
def sensibilizaciones_index():
    return render_template('sensibilizaciones/index.html')


@comunitario_bp.route('/sensibilizaciones/nuevo', methods=['POST'])
def sensibilizacion_nuevo():
    flash('Módulo de sensibilizaciones pendiente de implementación.', 'info')
    return redirect(url_for('sensibilizacion.index'))


@comunitario_bp.route('/sensibilizaciones/<int:sensibilizacion_id>/estado', methods=['POST'])
def sensibilizacion_cambiar_estado(sensibilizacion_id):
    flash('Módulo de sensibilizaciones pendiente de implementación.', 'info')
    return redirect(url_for('sensibilizacion.index'))