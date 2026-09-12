import csv
from io import StringIO

from flask import Response


def respuesta_csv(nombre_archivo, encabezados, filas):
    """Construye una descarga CSV UTF-8 compatible con Excel."""
    salida = StringIO()
    salida.write('\ufeff')
    escritor = csv.writer(salida)
    escritor.writerow(encabezados)
    escritor.writerows(filas)
    return Response(
        salida.getvalue(),
        mimetype='text/csv; charset=utf-8',
        headers={
            'Content-Disposition': f'attachment; filename={nombre_archivo}',
        },
    )
