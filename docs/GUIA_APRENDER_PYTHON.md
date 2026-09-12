# Guía para aprender Python con el proyecto ONCC

Esta guía recorre los conceptos de Python usando el código real del proyecto como ejemplo. Está pensada para alguien que ya conoce los fundamentos de Python y quiere ver cómo se aplican en una aplicación Flask real.

---

## Índice de conceptos

| # | Concepto | Categoría | Archivo clave |
|---|----------|-----------|---------------|
| 1 | App Factory + Blueprints | Arquitectura | `app/__init__.py` |
| 2 | Modelos ORM (SQLAlchemy) | Base de datos | `app/models/usuario.py` |
| 3 | Decoradores personalizados | Funciones | `app/utils/authorization.py` |
| 4 | `@property` y `synonym` | OOP / ORM | `app/models/usuario.py` |
| 5 | List Comprehension | Estructuras de datos | `app/blueprints/core/controllers/roles.py` |
| 6 | Context Managers (`with`) | Recursos | `app/cli.py` |
| 7 | Type Hints | Anotaciones | `app/services/gestor_sesion.py` |
| 8 | Variables de entorno + `dotenv` | Configuración | `config.py` |
| 9 | Manejo de excepciones + rollback | Errores | `app/services/auditoria.py` |
| 10 | `@staticmethod` | OOP | `app/services/notificacion.py` |
| 11 | `lambda` para defaults dinámicos | Funciones | `app/models/password_reset.py` |
| 12 | `getattr()` con fallback | Introspección | `app/blueprints/core/controllers/usuarios.py` |
| 13 | Flask-Login y autenticación | Seguridad | `app/blueprints/core/controllers/auth.py` |
| 14 | Comandos CLI personalizados | CLI | `app/cli.py` |
| 15 | Flask-WTF Forms + Validadores | Formularios | `app/blueprints/core/forms.py` |
| 16 | Relación Many-to-Many | ORM | `app/models/role.py` |
| 17 | Subida de archivos | I/O | `app/blueprints/monitoreo/controllers/actividades.py` |
| 18 | Pytest Fixtures | Testing | `tests/test_auth_integration.py` |
| 19 | `__repr__` y `super().__init__()` | Dunder methods | `app/models/role.py` |
| 20 | `Counter` de Collections | Estructuras de datos | `app/__init__.py` |

---

## 1. App Factory + Blueprints

### Concepto

Flask permite crear la aplicación dentro de una función (`create_app()`) en lugar de hacerlo globalmente. Esto se llama **Application Factory** y permite tener múltiples instancias (desarrollo, testing, producción).

Los **Blueprints** agrupan rutas por dominio funcional.

### Código en el proyecto

```python
# app/__init__.py:22-24
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    # ... extensiones, blueprints, rutas ...
    return app
```

```python
# run.py:1-4
from app import create_app
app = create_app()
```

```python
# app/blueprints/core/__init__.py:1-5
from flask import Blueprint
core_bp = Blueprint('core', __name__)

# Luego se registra en create_app():
# app.register_blueprint(core_bp)
```

### Para aprender más

Busca en el proyecto: `Blueprint(` y `register_blueprint(` para ver todos los módulos.

---

## 2. Modelos ORM (SQLAlchemy)

### Concepto

Cada tabla de la BD se representa como una clase Python que hereda de `db.Model`. Las columnas son atributos de clase del tipo `db.Column`.

### Código en el proyecto

```python
# app/models/usuario.py:6-17
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'

    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(30), nullable=False)
    clave_usuario = db.Column('clave usuario', db.String(255), nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey('roles.id_rol'), nullable=False)
    correo = db.Column(db.String(100), nullable=True)
    estatus = db.Column(db.Boolean, default=True)

    role = db.relationship('Role', back_populates='usuarios')
```

### Para aprender más

Busca `db.Column(` en `app/models/` y fíjate en los distintos tipos (`Integer`, `String`, `DateTime`, `Boolean`, `Text`, `ARRAY`).

---

## 3. Decoradores personalizados

### Concepto

Un decorador es una función que envuelve a otra para extender su comportamiento. Python permite crear **decoradores con argumentos** usando 3 niveles de anidación (función que devuelve un decorador que devuelve una wrapper).

### Código en el proyecto

```python
# app/utils/authorization.py:6-33
def role_required(*role_names):
    """Decorator: permite acceso solo si el usuario tiene alguno de los roles listados."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Debe iniciar sesión...', 'error')
                return redirect(url_for('auth.login'))
            for rn in role_names:
                if current_user.has_role(rn):
                    return f(*args, **kwargs)
            return redirect(url_for('dashboard'))
        return wrapped
    return decorator
```

Uso:
```python
@core_bp.route('/admin/usuarios/')
@login_required
@role_required('Superusuario', 'Administrador', 'Director Regional')
def usuario_index():
    ...
```

### Para aprender más

Busca `@role_required(` y `@login_required` en los controladores para ver dónde se aplican.

---

## 4. `@property` y `synonym`

### Concepto

- **`@property`**: convierte un método en un atributo de solo lectura, permitiendo lógica al acceder a él.
- **`synonym`**: permite que dos nombres de atributo apunten a la misma columna.

### Código en el proyecto

```python
# app/models/usuario.py:19-27
id = synonym('id_usuario')
nombre = synonym('nombre_usuario')

@property
def rol(self):
    return self.role.nombre if self.role else 'Sin Rol'
```

Esto permite usar `usuario.id` en lugar de `usuario.id_usuario`, y `usuario.rol` devuelve el nombre del rol en lugar del ID numérico.

### Para aprender más

Busca `@property` y `synonym(` en `app/models/` para ver otros ejemplos.

---

## 5. List Comprehension

### Concepto

Construye una nueva lista aplicando una expresión a cada elemento de un iterable, opcionalmente filtrando con `if`.

### Código en el proyecto

```python
# app/blueprints/core/controllers/roles.py:113
seleccion = request.form.getlist('permisos')
rol.permissions = [Permission.query.get(int(pid)) for pid in seleccion if pid.isdigit()]
```

Filtra solo los IDs numéricos de `seleccion` y convierte cada uno en un objeto `Permission`.

### Para aprender más

Busca `[` en los controladores para identificar otros usos de list comprehension.

---

## 6. Context Managers (`with`)

### Concepto

El bloque `with` asegura que un recurso se limpie automáticamente al salir, incluso si hay errores. Flask usa `app.app_context()` para hacer disponible `current_app` y `db.session` fuera de una petición HTTP.

### Código en el proyecto

```python
# app/cli.py:22-24
def do_seed():
    with current_app.app_context():
        director_role = Role.query.filter_by(nombre=super_role_name).first()
        # ...

# tests/test_auth_integration.py:16-19
with app.app_context():
    db.create_all()
    yield app
    db.session.remove()
    db.drop_all()
```

### Para aprender más

Busca `with current_app.app_context():` en el proyecto.

---

## 7. Type Hints

### Concepto

Python permite anotar tipos de parámetros y valores de retorno. Son opcionales pero mejoran la legibilidad y permiten a los IDEs hacer autocompletado.

### Código en el proyecto

```python
# app/services/gestor_sesion.py:17-34
def iniciar_sesion(self, usuario: Usuario):
    login_user(usuario)

def solicitar_recuperacion(self, correo: str):
    # ...

def confirmar_restauracion(self, token: str, nueva_password: str) -> bool:
    # ...
```

### Para aprender más

Busca `->` y `: str`, `: int`, `: bool` en los archivos `.py`.

---

## 8. Variables de entorno + `dotenv`

### Concepto

Usar `os.environ.get()` con `python-dotenv` permite cargar configuración desde un archivo `.env` sin modificar el código.

### Código en el proyecto

```python
# config.py:7-8, 35-40
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'oncc-clave-super-secreta-...'
    SQLALCHEMY_DATABASE_URI = build_database_uri()
```

```python
# app/cli.py:62-68
director_email = os.environ.get('ADMIN_EMAIL', 'director@oncc.gob.ve')
pw = os.environ.get('ADMIN_PASSWORD')
if not pw:
    pw = secrets.token_urlsafe(8)
```

### Para aprender más

Busca `os.environ.get(` en el proyecto para ver qué variables se leen.

---

## 9. Manejo de excepciones + rollback

### Concepto

`try/except` captura errores. `db.session.rollback()` deshace cambios en la BD cuando ocurre un error, dejando la sesión limpia.

### Código en el proyecto

```python
# app/services/auditoria.py:14-18
try:
    db.session.add(bit)
    db.session.commit()
except Exception:
    db.session.rollback()  # Si falla la auditoría, no rompe el flujo principal
```

```python
# app/blueprints/core/controllers/divulgacion.py:42-43
try:
    publicaciones = Publicacion.query.filter_by(estado='publicado').all()
except OperationalError:
    db.session.rollback()
```

### Para aprender más

Busca `try:` y `except` en los archivos de `app/`.

---

## 10. `@staticmethod`

### Concepto

Un método estático pertenece a la clase, no a una instancia. No recibe `self` ni `cls`. Se usa cuando la lógica no depende del estado del objeto.

### Código en el proyecto

```python
# app/services/notificacion.py:5-11
class ServicioNotificacion:
    @staticmethod
    def disparar_a_main_page(publicacion):
        # stub for external notification
        return True

    @staticmethod
    def compartir_en_redes(publicacion):
        return True
```

Se usa como `ServicioNotificacion.disparar_a_main_page(publicacion)` sin instanciar la clase.

---

## 11. `lambda` para defaults dinámicos

### Concepto

`lambda` crea una función anónima en una sola línea. Se usa aquí para que el default de una columna se calcule en el momento de insertar la fila, no al definir la clase.

### Código en el proyecto

```python
# app/models/password_reset.py:12-15
expiracion = db.Column(
    db.DateTime,
    nullable=False,
    default=lambda: datetime.utcnow() + timedelta(hours=2)
)
```

Cada nuevo token expira 2 horas después del momento exacto de creación.

---

## 12. `getattr()` con fallback

### Concepto

`getattr(objeto, 'atributo', default)` intenta acceder a un atributo de forma segura. Si no existe, devuelve el valor por defecto en lugar de lanzar `AttributeError`.

### Código en el proyecto

```python
# app/blueprints/core/controllers/usuarios.py:57
user_rol = getattr(nuevo_usuario, 'rol', rol)
```

```python
# app/utils/authorization.py:18
user_role_field = (getattr(current_user, 'rol', '') or '').strip().lower()
```

Útil cuando el nombre de un atributo puede variar entre modelos o cuando trabajas con objetos que podrían no tener ese atributo.

---

## 13. Flask-Login y autenticación

### Concepto

Flask-Login maneja sesiones de usuario. El modelo debe heredar de `UserMixin`. Se usa `login_user()` para iniciar sesión y `@login_required` para proteger rutas.

### Código en el proyecto

```python
# app/__init__.py:17-18, 37-39
login_manager = LoginManager()
login_manager.login_view = 'core.login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))
```

```python
# app/blueprints/core/controllers/auth.py:44-46
if usuario.check_password(password):
    login_user(usuario)
    return redirect(url_for('dashboard'))
```

Protección de rutas:
```python
@core_bp.route('/admin/usuarios/')
@login_required
@role_required('Administrador', 'Director Regional')
def usuario_index():
    ...
```

---

## 14. Comandos CLI personalizados

### Concepto

Flask permite registrar comandos con `@app.cli.command()`, ejecutables como `flask seed` desde la terminal.

### Código en el proyecto

```python
# app/cli.py:9-13
def register_cli_commands(app):
    @app.cli.command('seed')
    def seed():
        """Seed initial data: roles, permissions and admin user."""
        do_seed()
```

Uso en terminal:
```bash
flask seed
flask assign-super-role
```

---

## 15. Flask-WTF Forms + Validadores

### Concepto

Los formularios son clases que heredan de `FlaskForm`. Cada campo tiene tipo y validadores encadenados.

### Código en el proyecto

```python
# app/blueprints/core/forms.py:6-15, 27-38
class LoginForm(FlaskForm):
    correo = StringField(
        'Correo institucional',
        validators=[
            DataRequired(message='Debe ingresar su correo institucional.'),
            Email(message='Ingrese un correo válido.'),
            Length(max=120)
        ],
    )
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6, max=128)])
```

Uso en el controlador:
```python
form = LoginForm()
if form.validate_on_submit():
    correo = form.correo.data.strip().lower()
    password = form.password.data
```

---

## 16. Relación Many-to-Many (SQLAlchemy)

### Concepto

Se usa una tabla intermedia (association table) para conectar dos tablas con relación muchos-a-muchos.

### Código en el proyecto

```python
# app/models/role.py:5-9
role_permissions = db.Table(
    'permiso',
    db.Column('id_modulo', db.Integer, db.ForeignKey('modulos.id_modulo')),
    db.Column('id_rol', db.Integer, db.ForeignKey('roles.id_rol')),
)

class Role(db.Model):
    __tablename__ = 'roles'
    permissions = db.relationship('Permission', secondary=role_permissions,
                                   back_populates='roles')

class Permission(db.Model):
    __tablename__ = 'modulos'
    roles = db.relationship('Role', secondary=role_permissions, back_populates='permissions')
```

Un rol puede tener muchos permisos, y un permiso puede estar en muchos roles.

---

## 17. Subida de archivos (`secure_filename`)

### Concepto

`secure_filename()` de Werkzeug sanitiza el nombre del archivo para evitar vulnerabilidades de path traversal.

### Código en el proyecto

```python
# app/blueprints/monitoreo/controllers/actividades.py:15-24
def _guardar_archivo(archivo, carpeta):
    if not archivo or not archivo.filename:
        return None
    nombre_archivo = secure_filename(archivo.filename)
    destino = os.path.join(current_app.root_path, 'static', 'uploads', carpeta)
    os.makedirs(destino, exist_ok=True)
    ruta_completa = os.path.join(destino, nombre_archivo)
    archivo.save(ruta_completa)
    return os.path.join('uploads', carpeta, nombre_archivo).replace('\\', '/')
```

---

## 18. Pytest Fixtures

### Concepto

`@pytest.fixture` crea recursos que se configuran antes y se limpian después de cada prueba. Ideal para crear una BD en memoria.

### Código en el proyecto

```python
# tests/test_auth_integration.py:8-27
@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
    })
    with app.app_context():
        db.create_all()
        yield app     # ← la prueba recibe este app
        db.session.remove()
        db.drop_all() # ← limpieza después de la prueba
```

---

## 19. `__repr__` y `super().__init__()`

### Concepto

- `__repr__` define cómo se representa un objeto como string (útil para debug).
- `super().__init__()` llama al constructor de la clase padre.

### Código en el proyecto

```python
# app/models/role.py:40-41
def __repr__(self):
    return f"<Role {self.nombre_rol}>"
```

```python
# app/models/role.py:24-30 (constructor personalizado)
def __init__(self, **kwargs):
    nombre = kwargs.pop('nombre', None)
    descripcion = kwargs.pop('descripcion', None)
    super().__init__(**kwargs)
    if nombre is not None:
        self.nombre_rol = nombre
    self._descripcion = descripcion or ''
```

---

## 20. `Counter` de Collections

### Concepto

`Counter` cuenta automáticamente elementos de un iterable. Es como un diccionario donde cada clave es un elemento y su valor es el conteo.

### Código en el proyecto

```python
# app/blueprints/core/controllers/divulgacion.py:45-47
from collections import Counter

publicados = Publicacion.query.filter(Publicacion.estado != 'borrador').all()
visitas_por_mes = Counter(p.mes for p in publicados if hasattr(p, 'mes') and p.mes)
```

---

## Resumen: flujo completo de una petición

```
Usuario hace clic en "Iniciar sesión"
        ↓
Flask recibe GET /auth/login
        ↓
app/__init__.py mapea la URL a auth.login (core_login)
        ↓
app/blueprints/core/controllers/auth.py procesa la ruta
  - Crea LoginForm
  - Renderiza auth/login.html
        ↓
Usuario llena el formulario y hace clic en "Ingresar"
        ↓
POST /auth/login → mismo controlador
  - form.validate_on_submit() → True
  - Usuario.query.filter_by(correo=...).first()
  - usuario.check_password(password)
  - login_user(usuario)  ← Flask-Login crea la sesión
  - redirect(url_for('dashboard'))
        ↓
GET /dashboard
  - @login_required verifica que el usuario está autenticado
  - Consultas a la BD (actividades, inventario, etc.)
  - render_template('dashboard.html', resumen=..., ...)
        ↓
Usuario ve el dashboard con datos de la BD
```

---

## Para practicar

1. **Crea un nuevo modelo**: añade una clase en `app/models/` y genera migración
2. **Crea un nuevo blueprint**: replica la estructura de `app/blueprints/core/`
3. **Agrega un endpoint**: añade una ruta nueva en un controlador existente
4. **Escribe un test**: copia el patrón de `tests/test_auth_integration.py`
5. **Crea un comando CLI**: agrega un `@app.cli.command` en `app/cli.py`
6. **Agrega un decorador**: haz un decorador que registre el tiempo de ejecución de cada ruta
