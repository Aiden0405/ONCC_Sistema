from functools import wraps
from flask import redirect, url_for, flash, current_app
from flask_login import current_user


SUPERUSER_ROLE_IDS = (1, 2)


def current_role_id(default=None):
    try:
        return int(getattr(current_user, 'id_rol', default))
    except (TypeError, ValueError):
        return default


def is_superuser():
    return current_role_id() in SUPERUSER_ROLE_IDS


def current_permission_names():
    if not current_user.is_authenticated:
        return []

    try:
        return list(getattr(current_user, 'permission_names', []))
    except Exception:
        return []


def has_permission(permission_name):
    if not current_user.is_authenticated:
        return False

    if is_superuser():
        return True

    try:
        return current_user.has_permission(permission_name)
    except Exception:
        return permission_name in current_permission_names()


def role_required(*role_names):
    """Decorator: permite acceso solo si el usuario tiene alguno de los roles listados."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Debe iniciar sesión para acceder a esta sección.', 'error')
                return redirect(url_for('auth.login'))

            # Si el usuario tiene el rol superusuario configurado, permitir siempre
            try:
                super_role = (current_app.config.get('SUPER_ROLE_NAME') or '').strip().lower()
                user_role_field = (getattr(current_user, 'rol', '') or '').strip().lower()
                if super_role and (user_role_field == super_role or current_user.has_role(super_role)):
                    return f(*args, **kwargs)
            except Exception:
                pass

            # Permitir si tiene alguno de los roles (revisar relación many-to-many).
            for rn in role_names:
                if current_user.has_role(rn):
                    return f(*args, **kwargs)

            # Sin permiso: redirigir sin flash (para evitar mensajes confusos).
            return redirect(url_for('dashboard'))

        return wrapped
    return decorator


def permission_required(*permission_names):
    """Decorator: permite acceso si el usuario tiene alguno de los permisos listados."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Debe iniciar sesión para acceder a esta sección.', 'error')
                return redirect(url_for('auth.login'))

            # Si el usuario tiene el rol superusuario configurado, permitir siempre
            try:
                super_role = (current_app.config.get('SUPER_ROLE_NAME') or '').strip().lower()
                user_role_field = (getattr(current_user, 'rol', '') or '').strip().lower()
                if super_role and (user_role_field == super_role or current_user.has_role(super_role)):
                    return f(*args, **kwargs)
            except Exception:
                pass

            for pn in permission_names:
                if has_permission(pn):
                    return f(*args, **kwargs)

            flash('No tiene permisos suficientes para acceder a esta sección.', 'error')
            return redirect(url_for('dashboard'))

        return wrapped
    return decorator
