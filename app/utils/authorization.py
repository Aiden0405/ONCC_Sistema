from functools import wraps
from flask import redirect, url_for, flash, current_app
from flask_login import current_user


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

            # Permitir si tiene alguno de los permisos
            for pn in permission_names:
                if current_user.has_permission(pn):
                    return f(*args, **kwargs)

            # Sin permiso: redirigir sin flash para no mostrar mensajes confusos
            return redirect(url_for('dashboard'))

            flash('No tiene permisos suficientes para acceder a esta sección.', 'error')
            return redirect(url_for('dashboard'))

        return wrapped
    return decorator
