# Diagramas de Secuencia - Modulos Core ONCC

Este documento contiene 8 diagramas de secuencia alineados al codigo real de los modulos:

- Gestion de Usuarios (4)
- Divulgacion (4)

Nota metodologica:
- No se incluyen vistas (HTML) como objetos del diagrama.
- Se modelan actor, controlador, servicios, modelos y base de datos.
- Se usa destroy cuando el objeto temporal termina su funcion en el flujo.

## Modulo: Gestion de Usuarios

### 1) Registrar Nuevo Usuario

```mermaid
sequenceDiagram
    actor SU as Super Usuario / Admin
    participant UCtrl as usuarios.usuario_nuevo()
    participant AuthZ as verificar_permiso_dinamico()
    participant User as Usuario
    participant Role as Role
    participant Audit as registrar_accion()
    participant DB as PostgreSQL(seguridad)

    SU->>UCtrl: POST /admin/usuarios/nuevo
    UCtrl->>AuthZ: gestionar_usuarios
    AuthZ->>DB: validar rol y permisos del operador
    DB-->>AuthZ: permitido
    AuthZ-->>UCtrl: OK

    UCtrl->>Role: Role.query.order_by(...)
    Role->>DB: SELECT roles
    DB-->>Role: roles
    Role-->>UCtrl: roles

    UCtrl->>User: Usuario.query.filter_by(correo)
    User->>DB: SELECT usuario por correo
    DB-->>User: no existe
    User-->>UCtrl: libre

    create participant NewUser as Usuario(nuevo)
    UCtrl->>NewUser: set_password(password)
    UCtrl->>DB: INSERT usuario
    UCtrl->>Audit: registrar_accion(Crear)
    Audit->>DB: INSERT bitacora
    UCtrl-->>SU: flash success + redirect index

    destroy NewUser
```

### 2) Modificar Usuario

```mermaid
sequenceDiagram
    actor SU as Super Usuario / Admin
    participant UCtrl as usuarios.usuario_editar()
    participant AuthZ as verificar_permiso_dinamico()
    participant User as Usuario
    participant Audit as registrar_accion()
    participant DB as PostgreSQL(seguridad)

    SU->>UCtrl: POST /admin/usuarios/{id}/editar
    UCtrl->>AuthZ: gestionar_usuarios
    AuthZ->>DB: validar permiso
    DB-->>AuthZ: permitido
    AuthZ-->>UCtrl: OK

    UCtrl->>User: Usuario.query.get_or_404(id)
    User->>DB: SELECT usuario objetivo
    DB-->>User: usuario
    User-->>UCtrl: objeto usuario

    alt operador sin jerarquia
        UCtrl-->>SU: abort 403
    else operador autorizado
        opt password nueva enviada
            UCtrl->>User: usuario.set_password(nueva_pass)
        end
        UCtrl->>DB: UPDATE usuario
        UCtrl->>Audit: registrar_accion(Modificar)
        Audit->>DB: INSERT bitacora
        UCtrl-->>SU: flash success
    end
```

### 3) Eliminar Usuario

```mermaid
sequenceDiagram
    actor SU as Super Usuario / Admin
    participant UCtrl as usuarios.usuario_eliminar()
    participant AuthZ as verificar_permiso_dinamico()
    participant User as Usuario
    participant Audit as registrar_accion()
    participant DB as PostgreSQL(seguridad)

    SU->>UCtrl: POST /admin/usuarios/{id}/eliminar
    UCtrl->>AuthZ: gestionar_usuarios
    AuthZ->>DB: validar permiso
    DB-->>AuthZ: permitido
    AuthZ-->>UCtrl: OK

    UCtrl->>User: Usuario.query.get_or_404(id)
    User->>DB: SELECT usuario objetivo
    DB-->>User: usuario
    User-->>UCtrl: usuario

    alt auto-eliminacion o jerarquia invalida
        UCtrl-->>SU: flash error + redirect
    else permitido
        UCtrl->>DB: DELETE usuario
        UCtrl->>Audit: registrar_accion(Eliminar)
        Audit->>DB: INSERT bitacora
        UCtrl-->>SU: flash success
    end
```

### 4) Gestionar Permisos de Rol (Control de Acceso)

```mermaid
sequenceDiagram
    actor SU as Super Usuario / Admin
    participant RCtrl as roles.rol_gestionar_permisos()
    participant AuthZ as verificar_permiso_dinamico()
    participant Role as Role
    participant Pivot as Permiso
    participant Perm as Permission
    participant Audit as registrar_accion()
    participant DB as PostgreSQL(seguridad)

    SU->>RCtrl: POST /admin/roles/{rol_id}/permisos
    RCtrl->>AuthZ: gestionar_usuarios
    AuthZ->>DB: validar permiso
    DB-->>AuthZ: permitido
    AuthZ-->>RCtrl: OK

    RCtrl->>Role: Role.query.get_or_404(rol_id)
    Role->>DB: SELECT rol
    DB-->>Role: rol
    Role-->>RCtrl: rol

    RCtrl->>Perm: Permission.query.order_by(...)
    Perm->>DB: SELECT modulos
    DB-->>Perm: lista permisos
    Perm-->>RCtrl: permisos

    RCtrl->>Pivot: Permiso.query.filter_by(id_rol).delete()
    Pivot->>DB: DELETE pivote permisos
    loop por cada permiso seleccionado
        create participant Rel as Permiso(new)
        RCtrl->>Rel: construir relacion id_rol-id_modulo
        RCtrl->>DB: INSERT pivote
        destroy Rel
    end

    RCtrl->>Audit: registrar_accion(ActualizarPermisos)
    Audit->>DB: INSERT bitacora
    RCtrl-->>SU: flash success
```

## Modulo: Divulgacion

### 1) Crear Publicacion

```mermaid
sequenceDiagram
    actor TE as Tecnico / Admin
    participant DCtrl as divulgacion.divulgacion_admin_nuevo()
    participant AuthZ as verificar_permiso_dinamico()
    participant Act as Actividad
    participant Pub as Publicacion
    participant Audit as registrar_accion()
    participant DB as PostgreSQL(sistema)

    TE->>DCtrl: GET/POST /admin/divulgacion/nuevo
    DCtrl->>AuthZ: crear_divulgaciones
    AuthZ->>DB: validar permiso rol
    DB-->>AuthZ: permitido
    AuthZ-->>DCtrl: OK

    DCtrl->>Act: Actividad.query.order_by(...).limit(300)
    Act->>DB: SELECT actividades origen
    DB-->>Act: lista actividades
    Act-->>DCtrl: opciones id_divulgacion

    alt no hay actividades
        DCtrl-->>TE: flash error + redirect index
    else hay actividades
        create participant NewPub as Publicacion(nueva)
        DCtrl->>NewPub: mapear campos formulario
        alt usuario con aprobar_divulgaciones o superuser
            DCtrl->>NewPub: estado=form.estado
        else tecnico operativo
            DCtrl->>NewPub: estado=borrador
        end
        DCtrl->>DB: INSERT publicacion
        DCtrl->>Audit: registrar_accion(Crear)
        Audit->>DB: INSERT bitacora
        DCtrl-->>TE: flash success
        destroy NewPub
    end
```

### 2) Editar Publicacion

```mermaid
sequenceDiagram
    actor TE as Tecnico / Admin
    participant DCtrl as divulgacion.divulgacion_admin_editar()
    participant AuthZ as verificar_permiso_dinamico()
    participant Pub as Publicacion
    participant Act as Actividad
    participant Audit as registrar_accion()
    participant DB as PostgreSQL(sistema)

    TE->>DCtrl: GET/POST /admin/divulgacion/{id}/editar
    DCtrl->>AuthZ: crear_divulgaciones
    AuthZ->>DB: validar permiso
    DB-->>AuthZ: permitido
    AuthZ-->>DCtrl: OK

    DCtrl->>Pub: Publicacion.query.get_or_404(id)
    Pub->>DB: SELECT publicacion
    DB-->>Pub: publicacion
    Pub-->>DCtrl: objeto pub

    DCtrl->>Act: cargar opciones de actividad
    Act->>DB: SELECT actividades
    DB-->>Act: lista
    Act-->>DCtrl: choices

    alt operador no autorizado por autoria/estado
        DCtrl-->>TE: flash error + redirect
    else autorizado
        DCtrl->>DB: UPDATE publicacion
        opt sin permiso de aprobacion
            DCtrl->>DB: forzar estado=borrador
        end
        DCtrl->>Audit: registrar_accion(Modificar)
        Audit->>DB: INSERT bitacora
        DCtrl-->>TE: flash success
    end
```

### 3) Aprobar Publicacion

```mermaid
sequenceDiagram
    actor AD as Admin aprobador
    participant DCtrl as divulgacion.divulgacion_admin_aprobar()
    participant AuthZ as verificar_permiso_dinamico()
    participant Pub as Publicacion
    participant Notify as ServicioNotificacion
    participant Audit as registrar_accion()
    participant DB as PostgreSQL(sistema)

    AD->>DCtrl: POST /admin/divulgacion/{id}/aprobar
    DCtrl->>AuthZ: aprobar_divulgaciones
    AuthZ->>DB: validar permiso
    DB-->>AuthZ: permitido
    AuthZ-->>DCtrl: OK

    DCtrl->>Pub: Publicacion.query.get_or_404(id)
    Pub->>DB: SELECT publicacion
    DB-->>Pub: publicacion
    Pub-->>DCtrl: pub

    DCtrl->>DB: UPDATE estado_publicacion=publicado, publicado_en=utcnow
    DCtrl->>Notify: disparar_a_main_page(pub)
    create participant Event as PublicacionEvento
    Notify-->>Event: construir payload de notificacion
    destroy Event
    DCtrl->>Audit: registrar_accion(Modificar)
    Audit->>DB: INSERT bitacora
    DCtrl-->>AD: flash success
```

### 4) Eliminar Publicacion

```mermaid
sequenceDiagram
    actor TE as Tecnico / Admin
    participant DCtrl as divulgacion.divulgacion_admin_eliminar()
    participant AuthZ as verificar_permiso_dinamico()
    participant Pub as Publicacion
    participant Audit as registrar_accion()
    participant DB as PostgreSQL(sistema)

    TE->>DCtrl: POST /admin/divulgacion/{id}/eliminar
    DCtrl->>AuthZ: crear_divulgaciones
    AuthZ->>DB: validar permiso
    DB-->>AuthZ: permitido
    AuthZ-->>DCtrl: OK

    DCtrl->>Pub: Publicacion.query.get_or_404(id)
    Pub->>DB: SELECT publicacion
    DB-->>Pub: publicacion
    Pub-->>DCtrl: pub

    alt sin autoria o contenido publicado sin privilegio
        DCtrl-->>TE: flash error + redirect
    else autorizado
        DCtrl->>DB: DELETE publicacion
        DCtrl->>Audit: registrar_accion(Eliminar)
        Audit->>DB: INSERT bitacora
        DCtrl-->>TE: flash success
    end
```
