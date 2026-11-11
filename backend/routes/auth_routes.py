
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from datetime import datetime

# Servicios
from services.auth_services import autenticar_usuario
from services.dashboard_service import obtener_resumen
from services.inventario_service import reponer_stock

# Permisos
from utils.permisos import login_requerido


# Blueprint de autenticación
auth_bp = Blueprint("auth", __name__)


# ==========================================
# INICIO DE SESIÓN
# ==========================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    # Si ya inició sesión, enviarlo al dashboard
    if "id_usuario" in session:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        contrasena = request.form.get("contrasena", "")

        # Validar campos
        if not email or not contrasena:
            flash("Completa todos los campos", "danger")
            return render_template("auth/login.html")

        # Verificar usuario en MySQL
        usuario = autenticar_usuario(email, contrasena)

        if usuario:

            # Crear sesión
            session.clear()

            session["id_usuario"] = usuario["id_usuario"]
            session["nombre_usuario"] = usuario["nombre_usuario"]
            session["rol"] = usuario["rol"]
            session.permanent = True

            # Redirigir al dashboard
            return redirect(url_for("auth.dashboard"))

        # Credenciales incorrectas
        flash(
            "Correo o contraseña incorrectos, o usuario inactivo",
            "danger"
        )

    return render_template("auth/login.html")


# ==========================================
# DASHBOARD / RESUMEN
# ==========================================

@auth_bp.route("/dashboard")
@login_requerido
def dashboard():

    # Consultar estadísticas reales de MySQL
    resumen = obtener_resumen()

    # Fecha actual
    fecha_actual = datetime.now().strftime("%d/%m/%Y")

    # Mostrar dashboard
    return render_template(
        "dashboard/index.html",
        resumen=resumen,
        fecha_actual=fecha_actual
    )


# ==========================================
# REPONER INVENTARIO
# ==========================================

@auth_bp.route(
    "/inventario/reponer/<int:id_producto>",
    methods=["POST"]
)
@login_requerido
def reponer_inventario(id_producto):

    # Solo el administrador puede modificar inventario
    if session.get("rol") != "administrador":
        flash(
            "No tienes permisos para modificar el inventario.",
            "danger"
        )
        return redirect(url_for("auth.dashboard"))

    try:
        # Obtener cantidad enviada desde el modal
        cantidad = int(request.form.get("cantidad", "0"))

        # Validar cantidad
        if cantidad <= 0:
            raise ValueError(
                "Debes ingresar una cantidad mayor que cero."
            )

        # Actualizar inventario en MySQL
        resultado = reponer_stock(
            id_producto,
            cantidad
        )

        # Mensaje de éxito
        flash(
            f'Se agregaron {cantidad} unidades a '
            f'{resultado["nombre"]}. '
            f'Nuevo stock: {resultado["stock_nuevo"]}.',
            "success"
        )

    except (ValueError, TypeError) as error:

        flash(
            str(error),
            "danger"
        )

    # Regresar al resumen
    return redirect(url_for("auth.dashboard"))


# ==========================================
# CERRAR SESIÓN
# ==========================================

@auth_bp.route("/logout", methods=["POST"])
@login_requerido
def logout():

    # Eliminar datos de sesión
    session.clear()

    # Regresar al login
    return redirect(url_for("auth.login"))
