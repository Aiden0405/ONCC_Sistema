from app import create_app

app = create_app()

with app.app_context():
    print("Inicializador de datos - use 'flask db' para migraciones.")
    print(f"Base de datos activa: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    print("Para crear las tablas use: flask db init && flask db migrate && flask db upgrade")
    # Ejecutar seed programáticamente si la función está disponible
    try:
        from app.cli import do_seed
        do_seed()
    except Exception as e:
        print('No se pudo ejecutar seed automáticamente:', e)