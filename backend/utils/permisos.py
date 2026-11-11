from functools import wraps
from flask import session, redirect, url_for, abort


def login_requerido(funcion):
    @wraps(funcion)
    def decorador(*args, **kwargs):
        if "id_usuario" not in session:
            return redirect(url_for("auth.login"))

        return funcion(*args, **kwargs)

    return decorador


def roles_requeridos(*roles):
    def decorador_roles(funcion):
        @wraps(funcion)
        def decorador(*args, **kwargs):
            if "id_usuario" not in session:
                return redirect(url_for("auth.login"))

            if session.get("rol") not in roles:
                abort(403)

            return funcion(*args, **kwargs)

        return decorador

    return decorador_roles

