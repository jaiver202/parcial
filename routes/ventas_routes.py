
from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, session, jsonify
)

from utils.permisos import login_requerido

from services.ventas_services import (
    obtener_catalogo,
    obtener_clientes_pos,
    guardar_producto,
    registrar_venta
)

from database.conexion import obtener_conexion


# ==========================================
# BLUEPRINT DE VENTAS
# ==========================================

ventas_bp = Blueprint(
    "ventas",
    __name__,
    url_prefix="/ventas"
)


# ==========================================
# 1. MOSTRAR VENTAS POS
# ==========================================

@ventas_bp.route("/")
@login_requerido
def index():

    return render_template(
        "ventas/index.html",
        productos=obtener_catalogo(),
        clientes=obtener_clientes_pos(),
        titulo_pagina="Ventas POS",
        fecha_actual=datetime.now().strftime("%d/%m/%Y")
    )


# ==========================================
# 2. REGISTRAR NUEVO PRODUCTO
# ==========================================

@ventas_bp.route("/producto/crear", methods=["POST"])
@login_requerido
def crear_producto():

    try:

        nombre = request.form.get("nombre", "").strip()

        precio = Decimal(
            request.form.get("precio", "0")
        )

        cantidad = int(
            request.form.get("cantidad", "0")
        )

        descripcion = request.form.get(
            "descripcion", ""
        ).strip()

        if (
            not nombre
            or len(nombre) > 100
            or not precio.is_finite()
            or precio <= 0
            or precio > Decimal("99999999.99")
            or cantidad < 0
        ):
            raise ValueError(
                "Verifica los datos del producto."
            )

        guardar_producto(
            nombre,
            precio,
            cantidad,
            descripcion
        )

        flash(
            "Producto registrado correctamente.",
            "success"
        )

    except (ValueError, InvalidOperation):

        flash(
            "Verifica el nombre, precio y existencias.",
            "danger"
        )

    return redirect(url_for("ventas.index"))


# ==========================================
# 3. EDITAR PRODUCTO
# ==========================================

@ventas_bp.route(
    "/producto/editar/<int:id_producto>",
    methods=["POST"]
)
@login_requerido
def editar_producto(id_producto):

    # Solo administradores pueden editar productos
    if session.get("rol") != "administrador":
        flash(
            "No tienes permisos para editar productos.",
            "danger"
        )
        return redirect(url_for("ventas.index"))

    try:

        # Obtener datos del formulario
        nombre = request.form.get(
            "nombre", ""
        ).strip()

        precio = Decimal(
            request.form.get("precio", "")
        )

        cantidad = int(
            request.form.get("stock", "")
        )

        descripcion = request.form.get(
            "descripcion", ""
        ).strip()

        # Validar datos
        if (
            not nombre
            or len(nombre) > 100
            or not precio.is_finite()
            or precio <= 0
            or precio > Decimal("99999999.99")
            or precio.as_tuple().exponent < -2
            or cantidad < 0
        ):
            raise ValueError(
                "Verifica el nombre, precio y stock."
            )

        # Conectar a MySQL
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        try:

            # Verificar producto
            cursor.execute("""
                SELECT id_producto
                FROM producto
                WHERE id_producto = %s
                FOR UPDATE
            """, (id_producto,))

            producto = cursor.fetchone()

            if not producto:
                raise ValueError(
                    "El producto no existe."
                )

            # Actualizar tabla producto
            cursor.execute("""
                UPDATE producto
                SET nombre_producto = %s,
                    precio = %s,
                    descripcion = %s
                WHERE id_producto = %s
            """, (
                nombre,
                precio,
                descripcion,
                id_producto
            ))

            # Consultar registros de stock
            cursor.execute("""
                SELECT id_stock
                FROM stock
                WHERE id_producto = %s
                FOR UPDATE
            """, (id_producto,))

            registros_stock = cursor.fetchall()

            if len(registros_stock) > 1:
                raise ValueError(
                    "El producto tiene varios registros "
                    "de stock. Revisa la base de datos."
                )

            if registros_stock:

                # Actualizar stock existente
                cursor.execute("""
                    UPDATE stock
                    SET cantidad_disponible = %s
                    WHERE id_stock = %s
                """, (
                    cantidad,
                    registros_stock[0]["id_stock"]
                ))

            else:

                # Crear stock si no existe
                cursor.execute("""
                    INSERT INTO stock (
                        id_producto,
                        cantidad_disponible
                    )
                    VALUES (%s, %s)
                """, (
                    id_producto,
                    cantidad
                ))

            conexion.commit()

        except Exception:
            conexion.rollback()
            raise

        finally:
            cursor.close()
            conexion.close()

        flash(
            "Producto actualizado correctamente.",
            "success"
        )

    except (ValueError, InvalidOperation, TypeError) as error:

        flash(
            str(error) or "Verifica los datos del producto.",
            "danger"
        )

    return redirect(url_for("ventas.index"))


# ==========================================
# 4. COBRAR Y GENERAR FACTURA
# ==========================================

@ventas_bp.route("/cobrar", methods=["POST"])
@login_requerido
def cobrar():

    datos = request.get_json(silent=True) or {}

    try:

        id_cliente = int(
            datos.get("id_cliente")
        )

        metodo_pago = datos.get(
            "metodo_pago", "Efectivo"
        )

        items = datos.get("items", [])

        if metodo_pago not in (
            "Efectivo",
            "Transferencia",
            "Tarjeta"
        ):
            raise ValueError(
                "Método de pago no válido."
            )

        if not isinstance(items, list) or not items:
            raise ValueError(
                "El pedido debe contener productos."
            )

        # Registrar venta en MySQL
        resultado = registrar_venta(
            id_cliente,
            session["id_usuario"],
            metodo_pago,
            items
        )

        id_venta = resultado["id_venta"]
        numero_factura = resultado["numero_factura"]

        return jsonify({
            "ok": True,
            "mensaje": "Venta registrada correctamente.",
            "numero_factura": numero_factura,
            "url_factura": url_for(
                "facturas.detalle",
                id_venta=id_venta,
                nueva=1
            )
        })

    except (ValueError, TypeError) as error:

        return jsonify({
            "ok": False,
            "mensaje": str(error)
        }), 400
