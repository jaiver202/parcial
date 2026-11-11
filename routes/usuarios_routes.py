
from datetime import datetime
from functools import wraps

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, session, abort
)
from mysql.connector import IntegrityError

from utils.permisos import login_requerido
from services.usuarios_services import (
    listar_usuarios,
    obtener_usuario,
    crear_usuario,
    actualizar_usuario,
    eliminar_usuario
)

usuarios_bp = Blueprint(
    "usuarios",
    __name__,
    url_prefix="/usuarios"
)


def administrador_requerido(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get("rol") != "administrador":
            abort(403)
        return func(*args, **kwargs)
    return wrapper


def validar_datos(formulario, creando=False):
    nombre = formulario.get("nombre_usuario", "").strip()
    email = formulario.get("email", "").strip().lower()
    contrasena = formulario.get("contrasena", "")
    rol = formulario.get("rol", "")
    estado = formulario.get("estado", "")

    if not nombre or len(nombre) > 50:
        raise ValueError("Nombre inválido.")

    if not email or len(email) > 100 or "@" not in email:
        raise ValueError("Correo inválido.")

    if rol not in ("administrador", "vendedor"):
        raise ValueError("Rol inválido.")

    if estado not in ("activo", "inactivo"):
        raise ValueError("Estado inválido.")

    if creando and not contrasena:
        raise ValueError("La contraseña es obligatoria.")

    if contrasena and len(contrasena) < 8:
        raise ValueError("La contraseña debe tener mínimo 8 caracteres.")

    # bcrypt admite máximo 72 bytes
    if contrasena and len(contrasena.encode("utf-8")) > 72:
        raise ValueError("La contraseña es demasiado larga.")

    return nombre, email, contrasena, rol, estado


@usuarios_bp.route("/")
@login_requerido
@administrador_requerido
def index():
    return render_template(
        "usuarios/index.html",
        usuarios=listar_usuarios(),
        titulo_pagina="Usuarios",
        fecha_actual=datetime.now().strftime("%d/%m/%Y")
    )


@usuarios_bp.route("/crear", methods=["POST"])
@login_requerido
@administrador_requerido
def crear():
    try:
        datos = validar_datos(request.form, creando=True)
        crear_usuario(*datos)
        flash("Usuario creado correctamente.", "success")

    except IntegrityError:
        flash("El correo ya está registrado.", "danger")
    except ValueError as error:
        flash(str(error), "danger")

    return redirect(url_for("usuarios.index"))


@usuarios_bp.route("/editar/<int:id_usuario>", methods=["POST"])
@login_requerido
@administrador_requerido
def editar(id_usuario):
    try:
        if not obtener_usuario(id_usuario):
            abort(404)

        datos = validar_datos(request.form)

        nombre, email, contrasena, rol, estado = datos

        # No desactivar ni quitar el rol a la propia cuenta
        if id_usuario == session["id_usuario"]:
            if rol != "administrador" or estado != "activo":
                raise ValueError(
                    "No puedes quitarte permisos ni desactivar tu cuenta."
                )

        actualizar_usuario(
            id_usuario, nombre, email,
            rol, estado, contrasena or None
        )

        if id_usuario == session["id_usuario"]:
            session["nombre_usuario"] = nombre

        flash("Usuario actualizado correctamente.", "success")

    except IntegrityError:
        flash("El correo ya pertenece a otro usuario.", "danger")
    except ValueError as error:
        flash(str(error), "danger")

    return redirect(url_for("usuarios.index"))


@usuarios_bp.route("/eliminar/<int:id_usuario>", methods=["POST"])
@login_requerido
@administrador_requerido
def eliminar(id_usuario):
    if id_usuario == session["id_usuario"]:
        flash("No puedes eliminar tu propia cuenta.", "danger")
        return redirect(url_for("usuarios.index"))

    try:
        eliminar_usuario(id_usuario)
        flash("Usuario eliminado correctamente.", "success")

    except IntegrityError:
        flash(
            "Este usuario tiene ventas registradas. "
            "Puedes desactivarlo en lugar de eliminarlo.",
            "warning"
        )

    return redirect(url_for("usuarios.index"))
