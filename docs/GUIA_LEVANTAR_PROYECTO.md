# Guía para levantar el proyecto ONCC Sistema

## 1. Requisitos previos

- **Python 3.10+** instalado
- **PostgreSQL 15+** instalado y corriendo en `localhost:5432`
- **Git** (opcional, para clonar)

---

## 2. Clonar e ir al proyecto

```bash
git clone <repo-url> ONCC_Sistema
cd ONCC_Sistema
```

---

## 3. Crear y activar entorno virtual

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

---

## 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 5. Configurar variables de entorno

Crear archivo `.env` (basado en `.env.example`):

```env
SECRET_KEY=una-clave-segura-aleatoria

DB_ENGINE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=oncc_sistema
DB_USER=postgres
DB_PASSWORD=tu_contraseña_postgres
```

Opcional: predefinir credenciales del admin inicial:

```env
ADMIN_EMAIL=director@oncc.gob.ve
ADMIN_PASSWORD=UnaClaveSegura123
```

---

## 6. Crear la base de datos en PostgreSQL

```bash
# Entrar a psql y ejecutar:
psql -U postgres
CREATE DATABASE oncc_sistema;
\q
```

---

## 7. Inicializar migraciones y crear tablas

```bash
flask db init
flask db migrate -m "Primera migracion"
flask db upgrade
```

---

## 8. Poblar datos iniciales (seed)

```bash
flask seed
```

Esto crea los roles (Director Regional, Administrador, Técnico), permisos y el usuario administrador.

---

## 9. (Opcional) Cargar respaldo de base de datos

Si existe `respaldo.sql`:

```bash
psql -U postgres -d oncc_sistema -f respaldo.sql
```

---

## 10. Ejecutar el servidor

```bash
python run.py
```

O usando Flask CLI:

```bash
flask run --debug --port 5000
```

El servidor se levanta en `http://127.0.0.1:5000`.

---

## 11. Acceder al sistema

| Ruta | Descripción |
|------|-------------|
| `http://127.0.0.1:5000/` | Página pública principal |
| `http://127.0.0.1:5000/auth/login` | Inicio de sesión |
| `http://127.0.0.1:5000/dashboard` | Dashboard (requiere login) |

---

## 12. Ejecutar pruebas

```bash
pytest tests/
```

---

## Comandos útiles

| Comando | Descripción |
|---------|-------------|
| `flask seed` | Poblar datos iniciales |
| `flask db migrate -m "mensaje"` | Crear nueva migración |
| `flask db upgrade` | Aplicar migraciones |
| `flask db downgrade` | Revertir última migración |
| `python run.py` | Iniciar servidor |

---

## Estructura del proyecto

```
ONCC_Sistema/
├── app/
│   ├── blueprints/       # Módulos (core, comunitario, logistica, mapas, monitoreo)
│   ├── models/           # Modelos SQLAlchemy
│   ├── services/         # Lógica de negocio (PDF, notificaciones, etc.)
│   ├── templates/        # Plantillas HTML (Jinja2)
│   ├── static/           # CSS, JS, imágenes
│   └── cli.py            # Comandos Flask personalizados
├── migrations/           # Migraciones de base de datos
├── config.py             # Configuración (base de datos, seguridad, etc.)
├── run.py                # Punto de entrada
├── requirements.txt      # Dependencias Python
├── respaldo.sql          # Backup de base de datos
└── opencode.json         # Configuración de opencode (proyecto)
```

---

## Registro de cambios realizados

### Configuración del proyecto
| Cambio | Archivo | Descripción |
|--------|---------|-------------|
| `.env` creado | `.env` | Variables de entorno con parámetros PostgreSQL |
| `config.py` actualizado | `config.py` | `build_database_uri()` ahora lee `DB_ENGINE`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` desde el `.env` en lugar de tenerlos hardcodeados |
| `opencode.json` creado | `opencode.json` | Configuración `permission: { "*": "ask" }` |
| Contraseña admin reseteada | — | Usuario `director@oncc.gob.ve` con contraseña `admin123` |
| Seed corregido | `app/cli.py` | `Usuario()` ya no usa `rol=` (propiedad de solo lectura), se pasa `id_rol=` directamente |

### Módulo Inventario — Editar equipo
| Cambio | Archivo | Detalle |
|--------|---------|---------|
| Función `editar()` | `app/blueprints/logistica/controllers/inventario.py:63-100` | Ruta POST que actualiza todos los campos del equipo, valida código duplicado (excepto sí mismo) y registra en bitácora |
| Import + ruta | `app/__init__.py:101,156` | `from ... import editar` y `add_url_rule` para `/inventario/<id>/editar` |
| Botón editar por fila | `app/templates/inventario/index.html:234-236` | Icono ✏️ en columna Acciones |
| Modal de edición | `app/templates/inventario/index.html:107-174` | Modal con campos precargados vía JS |
| Función `_serializar()` | `app/blueprints/logistica/controllers/inventario.py:13-23` | Convierte objetos SQLAlchemy a dict para JSON |
| Variable `inventario_json` | `app/blueprints/logistica/controllers/inventario.py:30` | Datos serializados pasados a la plantilla |

### Módulo Inventario — Eliminar equipo
| Cambio | Archivo | Detalle |
|--------|---------|---------|
| Función `eliminar()` | `app/blueprints/logistica/controllers/inventario.py:116-128` | Ruta POST que elimina el registro y lo audita en bitácora |
| Import + ruta | `app/__init__.py:100,157` | `from ... import eliminar` y `add_url_rule` para `/inventario/<id>/eliminar` |
| Botón eliminar por fila | `app/templates/inventario/index.html:237-239` | Icono 🗑️ en columna Acciones |
| Modal de confirmación | `app/templates/inventario/index.html:253-269` | Modal "¿Estás seguro de eliminar este equipo?" con botones Cancelar / Eliminar |
