from app import create_app

# Llamamos a la función que crea la aplicación con todas sus configuraciones
app = create_app()

if __name__ == '__main__':
    # Arrancamos el servidor de Flask.
    # debug=True es MUY importante ahora, porque si cambias un color en el HTML, 
    # el servidor se reinicia solo sin que tengas que pararlo manualmente.
    app.run(debug=True, port=5000)