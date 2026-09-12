import os
import calendar
from datetime import datetime,date
from flask import request, jsonify, current_app, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app import db
from app.models.clima import MapaClimatico, RegistroClimatico
from app.services.notificacion import ServicioNotificacion
from sqlalchemy.exc import SQLAlchemyError
from app.utils.authorization import verificar_permiso_dinamico

# Extensiones exclusivas para mapas climáticos (imágenes)
EXTENSIONES_MAPAS_CLIMATICOS = {'png', 'jpg', 'jpeg', 'svg', 'webp'}

def archivo_permitido(filename, extensiones_validas):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensiones_validas

@login_required
def mapas_climaticos_index():
    verificar_permiso_dinamico('ver_mapas_climaticos')
    return render_template('mapas/climaticos.html')

@login_required
def procesar_mapa_climatico():
    verificar_permiso_dinamico('registrar_mapas_climaticos')
    """ Procesa y almacena un nuevo mapa climático enfocado en formato de imagen """
    tipo_mapa = request.form.get('tipo_mapa')
    id_estado = request.form.get('id_estado')
    archivo = request.files.get('archivo_mapa')
    
    es_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json

    if not archivo or archivo.filename == '':
        msg = 'Debe adjuntar una imagen cartográfica válida.'
        return jsonify({'status': 'error', 'message': msg}), 400 if es_ajax else redirect(url_for('mapas.mapas_climaticos_index'))

    if not archivo_permitido(archivo.filename, EXTENSIONES_MAPAS_CLIMATICOS):
        msg = 'Formato no soportado. Suba PNG, JPG, JPEG, SVG o WEBP.'
        return jsonify({'status': 'error', 'message': msg}), 400 if es_ajax else redirect(url_for('mapas.mapas_climaticos_index'))

    try:
        filename = secure_filename(archivo.filename)
        filename_unico = f"climatico_{int(datetime.now().timestamp())}_{filename}"
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'mapas', 'climaticos')
        os.makedirs(upload_folder, exist_ok=True)
        ruta_guardado = os.path.join(upload_folder, filename_unico)
        
        archivo.save(ruta_guardado)
        url_relativa = f'uploads/mapas/climaticos/{filename_unico}'

        nuevo_mapa = MapaClimatico(
            id_estado=int(id_estado),
            tipo_de_mapa=tipo_mapa,
            url_mapa=url_relativa,
            fecha_creacion=datetime.now().date()
        )
        
        db.session.add(nuevo_mapa)
        db.session.commit()
        mensaje = 'Se registró un nuevo mapa climático.'
        ServicioNotificacion.notificar_por_permiso('gestionar_geomatica', mensaje, emisor_id=current_user.id_usuario)
        ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Mapas')

        msg = 'Mapa climático registrado exitosamente.'
        if es_ajax:
            return jsonify({'status': 'success', 'message': msg, 'mapa_id': nuevo_mapa.id_mapa_climatico}), 201
            
        flash(msg, 'success')
        return redirect(url_for('mapas.mapas_climaticos_index'))

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@login_required
def listar_mapas_climaticos():
    verificar_permiso_dinamico('ver_mapas_climaticos')
    """ Devuelve el listado de mapas climáticos para la tabla dinámica """
    estado_id = request.args.get('estado', type=int)
    
    query = db.session.query(MapaClimatico)
    if estado_id:
        query = query.filter(MapaClimatico.id_estado == estado_id)
        
    mapas = query.order_by(MapaClimatico.fecha_creacion.desc()).all()
    
    resultados = [{
        'id': m.id_mapa_climatico,
        'tipo_de_mapa': m.tipo_de_mapa,
        'url_mapa': m.url_mapa,
        'fecha_creacion': m.fecha_creacion.isoformat()
    } for m in mapas]
    
    return jsonify(resultados), 200
@login_required
def actualizar_mapa_climatico(mapa_id):
    verificar_permiso_dinamico('editar_mapas_climaticos')
    mapa = MapaClimatico.query.get_or_404(mapa_id)
    data = request.get_json() if request.is_json else request.form

    try:
        mapa.nombre = data.get('nombre', mapa.nombre)
        mapa.descripcion = data.get('descripcion', mapa.descripcion)
        # Añade aquí los demás campos requeridos de tu modelo
        
        db.session.commit()
        mensaje = f'Se actualizó el mapa climático #{mapa_id}.'
        ServicioNotificacion.notificar_por_permiso('gestionar_geomatica', mensaje, emisor_id=current_user.id_usuario)
        ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Mapas')
        return jsonify({'status': 'success', 'mensaje': 'Mapa climático actualizado correctamente.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'mensaje': f'Error al actualizar: {str(e)}'}), 500
@login_required
def eliminar_mapa_climatico(mapa_id):
    verificar_permiso_dinamico('eliminar_mapas_climaticos')
    """ Elimina el registro y el archivo físico del mapa climático """
    mapa = MapaClimatico.query.get_or_404(mapa_id)
    try:
        ruta_fisica = os.path.join(current_app.root_path, 'static', mapa.url_mapa)
        
        db.session.delete(mapa)
        db.session.commit()
        mensaje = f'Se eliminó el mapa climático #{mapa_id}.'
        ServicioNotificacion.notificar_por_permiso('gestionar_geomatica', mensaje, emisor_id=current_user.id_usuario)
        ServicioNotificacion.crear_aviso(id_usuario=current_user.id_usuario, mensaje=mensaje, categoria='Mapas')
        
        if os.path.exists(ruta_fisica):
            try: os.remove(ruta_fisica)
            except OSError: pass
            
        return jsonify({'status': 'success', 'message': 'Mapa climático eliminado.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
def registrar_mes_climatico():
  try:
    # 1. Extracción y validación de parámetros principales
    id_equipo = request.form.get('id_equipo', type=int)
    anio = request.form.get('anio', type=int)
    mes = request.form.get('mes', type=int)
    id_mapa_climatico = request.form.get(
        'id_mapa_climatico', type=int, default=None
    )

    if not id_equipo or not anio or not mes:
      return (
          jsonify({
              'status': 'error',
              'message': 'Debe seleccionar un equipo, año y mes válidos.',
          }),
          400,
      )

    if not (1 <= mes <= 12):
      return (
          jsonify({
              'status': 'error',
              'message': 'El mes ingresado no es válido.',
          }),
          400,
      )

    hoy = date.today()

    # 2. Días exactos del mes (calendar.monthrange calcula bisiestos automáticamente)
    _, total_dias = calendar.monthrange(anio, mes)

    # 3. Procesar día por día
    for dia in range(1, total_dias + 1):
      # Construcción del objeto fecha
      fecha_actual = date(anio, mes, dia)

      # Validación: No permitir guardar días futuros
      if fecha_actual > hoy:
        db.session.rollback()
        return (
            jsonify({
                'status': 'error',
                'message': (
                    f'El día {dia}/{mes}/{anio} es una fecha futura y no se'
                    ' puede registrar.'
                ),
            }),
            400,
        )

      # Extraer valores del formulario
      temp_raw = request.form.get(f'temp_{dia}')
      prec_raw = request.form.get(f'prec_{dia}')
      viento_raw = request.form.get(f'viento_{dia}')
      hum_raw = request.form.get(f'hum_{dia}')

      # Validación de campos requeridos (Garantiza nullable=False)
      if any(
          v is None or str(v).strip() == ''
          for v in [temp_raw, prec_raw, viento_raw, hum_raw]
      ):
        db.session.rollback()
        return (
            jsonify({
                'status': 'error',
                'message': (
                    f'Faltan datos en el día {dia}. Todos los campos son'
                    ' obligatorios.'
                ),
            }),
            400,
        )

      # Conversión a flotantes y comprobación de tipo
      try:
        temp = float(temp_raw)
        prec = float(prec_raw)
        viento = float(viento_raw)
        hum = float(hum_raw)
      except ValueError:
        db.session.rollback()
        return (
            jsonify({
                'status': 'error',
                'message': (
                    f'Los valores ingresados para el día {dia} deben ser'
                    ' numéricos.'
                ),
            }),
            400,
        )

      # Validaciones de rangos meteorológicos lógicos
      if not (-60.0 <= temp <= 60.0):
        db.session.rollback()
        return (
            jsonify({
                'status': 'error',
                'message': (
                    f'Temperatura fuera de rango el día {dia} ({temp}°C).'
                ),
            }),
            400,
        )

      if prec < 0 or viento < 0:
        db.session.rollback()
        return (
            jsonify({
                'status': 'error',
                'message': (
                    f'Precipitaciones o vientos no pueden ser negativos en el'
                    f' día {dia}.'
                ),
            }),
            400,
        )

      if not (0.0 <= hum <= 100.0):
        db.session.rollback()
        return (
            jsonify({
                'status': 'error',
                'message': (
                    f'La humedad del día {dia} ({hum}%) debe estar entre 0 y'
                    ' 100.'
                ),
            }),
            400,
        )

      # 4. Upsert: Insertar o Actualizar según la clave (fecha_registro + id_equipo)
      registro = RegistroClimatico.query.filter_by(
          fecha_registro=fecha_actual, id_equipo=id_equipo
      ).first()

      if registro:
        registro.temperatura = temp
        registro.precipitaciones = prec
        registro.vientos = viento
        registro.humedad = hum
        if id_mapa_climatico:
          registro.id_mapa_climatico = id_mapa_climatico
      else:
        nuevo_registro = RegistroClimatico(
            fecha_registro=fecha_actual,
            id_equipo=id_equipo,
            id_mapa_climatico=id_mapa_climatico,
            temperatura=temp,
            precipitaciones=prec,
            vientos=viento,
            humedad=hum,
        )
        db.session.add(nuevo_registro)

    db.session.commit()
    return jsonify({
        'status': 'success',
        'message': (
            f'Se registraron correctamente los {total_dias} días del mes'
            f' {mes}/{anio}.'
        ),
    })

  except SQLAlchemyError as e:
    db.session.rollback()
    print(f'Error BD: {str(e)}')
    return (
        jsonify({
            'status': 'error',
            'message': (
                'Error de base de datos al intentar procesar los registros.'
            ),
        }),
        500,
    )
  except Exception as e:
    db.session.rollback()
    print(f'Error no controlado: {str(e)}')
    return (
        jsonify(
            {'status': 'error', 'message': f'Error interno del servidor: {str(e)}'}
        ),
        500,
    )
  try:
    # 1. Extracción y validación de parámetros principales
    id_equipo = request.form.get('id_equipo', type=int)
    anio = request.form.get('anio', type=int)
    mes = request.form.get('mes', type=int)
    id_mapa_climatico = request.form.get(
        'id_mapa_climatico', type=int, default=None
    )

    if not id_equipo or not anio or not mes:
      return (
          jsonify({
              'status': 'error',
              'message': 'Debe seleccionar un equipo, año y mes válidos.',
          }),
          400,
      )

    if not (1 <= mes <= 12):
      return (
          jsonify({
              'status': 'error',
              'message': 'El mes ingresado no es válido.',
          }),
          400,
      )

    hoy = date.today()

    # 2. Días exactos del mes (calendar.monthrange calcula bisiestos automáticamente)
    _, total_dias = calendar.monthrange(anio, mes)

    # 3. Procesar día por día
    for dia in range(1, total_dias + 1):
      # Construcción del objeto fecha
      fecha_actual = date(anio, mes, dia)

      # Validación: No permitir guardar días futuros
      if fecha_actual > hoy:
        db.session.rollback()
        return (
            jsonify({
                'status': 'error',
                'message': (
                    f'El día {dia}/{mes}/{anio} es una fecha futura y no se'
                    ' puede registrar.'
                ),
            }),
            400,
        )

      # Extraer valores del formulario
      temp_raw = request.form.get(f'temp_{dia}')
      prec_raw = request.form.get(f'prec_{dia}')
      viento_raw = request.form.get(f'viento_{dia}')
      hum_raw = request.form.get(f'hum_{dia}')

      # Validación de campos requeridos (Garantiza nullable=False)
      if any(
          v is None or str(v).strip() == ''
          for v in [temp_raw, prec_raw, viento_raw, hum_raw]
      ):
        db.session.rollback()
        return (
            jsonify({
                'status': 'error',
                'message': (
                    f'Faltan datos en el día {dia}. Todos los campos son'
                    ' obligatorios.'
                ),
            }),
            400,
        )

      # Conversión a flotantes y comprobación de tipo
      try:
        temp = float(temp_raw)
        prec = float(prec_raw)
        viento = float(viento_raw)
        hum = float(hum_raw)
      except ValueError:
        db.session.rollback()
        return (
            jsonify({
                'status': 'error',
                'message': (
                    f'Los valores ingresados para el día {dia} deben ser'
                    ' numéricos.'
                ),
            }),
            400,
        )

      # Validaciones de rangos meteorológicos lógicos
      if not (-60.0 <= temp <= 60.0):
        db.session.rollback()
        return (
            jsonify({
                'status': 'error',
                'message': (
                    f'Temperatura fuera de rango el día {dia} ({temp}°C).'
                ),
            }),
            400,
        )

      if prec < 0 or viento < 0:
        db.session.rollback()
        return (
            jsonify({
                'status': 'error',
                'message': (
                    f'Precipitaciones o vientos no pueden ser negativos en el'
                    f' día {dia}.'
                ),
            }),
            400,
        )

      if not (0.0 <= hum <= 100.0):
        db.session.rollback()
        return (
            jsonify({
                'status': 'error',
                'message': (
                    f'La humedad del día {dia} ({hum}%) debe estar entre 0 y'
                    ' 100.'
                ),
            }),
            400,
        )

      # 4. Upsert: Insertar o Actualizar según la clave (fecha_registro + id_equipo)
      registro = RegistroClimatico.query.filter_by(
          fecha_registro=fecha_actual, id_equipo=id_equipo
      ).first()

      if registro:
        registro.temperatura = temp
        registro.precipitaciones = prec
        registro.vientos = viento
        registro.humedad = hum
        if id_mapa_climatico:
          registro.id_mapa_climatico = id_mapa_climatico
      else:
        nuevo_registro = RegistroClimatico(
            fecha_registro=fecha_actual,
            id_equipo=id_equipo,
            id_mapa_climatico=id_mapa_climatico,
            temperatura=temp,
            precipitaciones=prec,
            vientos=viento,
            humedad=hum,
        )
        db.session.add(nuevo_registro)

    db.session.commit()
    return jsonify({
        'status': 'success',
        'message': (
            f'Se registraron correctamente los {total_dias} días del mes'
            f' {mes}/{anio}.'
        ),
    })

  except SQLAlchemyError as e:
    db.session.rollback()
    print(f'Error BD: {str(e)}')
    return (
        jsonify({
            'status': 'error',
            'message': (
                'Error de base de datos al intentar procesar los registros.'
            ),
        }),
        500,
    )
  except Exception as e:
    db.session.rollback()
    print(f'Error no controlado: {str(e)}')
    return (
        jsonify(
            {'status': 'error', 'message': f'Error interno del servidor: {str(e)}'}
        ),
        500,
    )
# 1. READ (Cargar / Consultar datos guardados de un mes)
@login_required
def cargar_mes_climatico():
  id_equipo = request.args.get('id_equipo', type=int)
  anio = request.args.get('anio', type=int)
  mes = request.args.get('mes', type=int)

  if not all([id_equipo, anio, mes]):
    return (
        jsonify({'status': 'error', 'message': 'Faltan datos de consulta.'}),
        400,
    )

  # Calcular rango de fechas del mes
  _, total_dias = calendar.monthrange(anio, mes)
  fecha_inicio = date(anio, mes, 1)
  fecha_fin = date(anio, mes, total_dias)

  # Buscar registros existentes
  registros = (
      RegistroClimatico.query.filter(
          RegistroClimatico.id_equipo == id_equipo,
          RegistroClimatico.fecha_registro.between(fecha_inicio, fecha_fin),
      )
      .order_by(RegistroClimatico.fecha_registro.asc())
      .all()
  )

  # Mapear resultado para el frontend
  datos = [
      {
          'dia': r.fecha_registro.day,
          'temperatura': float(r.temperatura),
          'precipitaciones': float(r.precipitaciones),
          'vientos': float(r.vientos),
          'humedad': float(r.humedad),
      }
      for r in registros
  ]

  return jsonify({'status': 'success', 'registros': datos})

# 2. UPDATE (Actualizar registros existentes de un mes)
@login_required
def actualizar_mes_climatico():
    try:
        id_equipo = request.form.get('id_equipo', type=int)
        anio = request.form.get('anio', type=int)
        mes = request.form.get('mes', type=int)

        if not all([id_equipo, anio, mes]):
            return jsonify({'status': 'error', 'message': 'Faltan datos obligatorios.'}), 400

        _, total_dias = calendar.monthrange(anio, mes)

        for dia in range(1, total_dias + 1):
            temp = request.form.get(f'temp_{dia}', type=float)
            prec = request.form.get(f'prec_{dia}', type=float)
            viento = request.form.get(f'viento_{dia}', type=float)
            hum = request.form.get(f'hum_{dia}', type=float)

            fecha = date(anio, mes, dia)
            registro = RegistroClimatico.query.filter_by(
                id_equipo=id_equipo,
                fecha_registro=fecha
            ).first()

            if registro:
                registro.temperatura = temp
                registro.precipitaciones = prec
                registro.vientos = viento
                registro.humedad = hum

        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Registros actualizados correctamente.'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


# 3. DELETE (Eliminar todo el mes registrado de un equipo)
@login_required
def eliminar_mes_climatico():
    try:
        id_equipo = request.values.get('id_equipo', type=int)
        anio = request.values.get('anio', type=int)
        mes = request.values.get('mes', type=int)

        if not all([id_equipo, anio, mes]):
            return jsonify({'status': 'error', 'message': 'Faltan parámetros para eliminar.'}), 400

        borrados = RegistroClimatico.query.filter(
            RegistroClimatico.id_equipo == id_equipo,
            db.extract('year', RegistroClimatico.fecha_registro) == anio,
            db.extract('month', RegistroClimatico.fecha_registro) == mes
        ).delete(synchronize_session=False)

        db.session.commit()
        return jsonify({'status': 'success', 'message': f'Se eliminaron {borrados} registros del mes.'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500