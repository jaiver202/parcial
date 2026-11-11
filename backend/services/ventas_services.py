
from decimal import Decimal
from uuid import uuid4

from database.conexion import obtener_conexion


def obtener_catalogo():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                p.id_producto,
                p.nombre_producto,
                p.precio,
                p.descripcion,
                COALESCE(SUM(s.cantidad_disponible), 0)
                    AS cantidad_disponible
            FROM producto p
            LEFT JOIN stock s
                ON p.id_producto = s.id_producto
            GROUP BY p.id_producto,
                     p.nombre_producto,
                     p.precio,
                     p.descripcion
            ORDER BY p.id_producto DESC
        """)
        return cursor.fetchall()

    finally:
        cursor.close()
        conexion.close()


def obtener_clientes_pos():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT id_cliente, nombre
            FROM cliente
            ORDER BY nombre
        """)
        return cursor.fetchall()

    finally:
        cursor.close()
        conexion.close()


def guardar_producto(nombre, precio, cantidad, descripcion):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        conexion.start_transaction()

        cursor.execute("""
            INSERT INTO producto
            (nombre_producto, precio, descripcion)
            VALUES (%s, %s, %s)
        """, (nombre, precio, descripcion))

        id_producto = cursor.lastrowid

        cursor.execute("""
            INSERT INTO stock
            (id_producto, cantidad_disponible)
            VALUES (%s, %s)
        """, (id_producto, cantidad))

        conexion.commit()
        return id_producto

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()


def registrar_venta(id_cliente, id_usuario, metodo_pago, items):
    if not items:
        raise ValueError("El pedido está vacío.")

    if metodo_pago not in ("Efectivo", "Transferencia", "Tarjeta"):
        raise ValueError("Método de pago no válido.")

    cantidades = {}

    for item in items:
        id_producto = int(item["id_producto"])
        cantidad = int(item["cantidad"])

        if id_producto <= 0 or cantidad <= 0:
            raise ValueError("Cantidad o producto no válido.")

        cantidades[id_producto] = (
            cantidades.get(id_producto, 0) + cantidad
        )

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        conexion.start_transaction()

        cursor.execute("""
            SELECT id_cliente FROM cliente
            WHERE id_cliente = %s
        """, (id_cliente,))

        if not cursor.fetchone():
            raise ValueError("Selecciona un cliente válido.")

        detalles = []
        total = Decimal("0.00")

        for id_producto in sorted(cantidades):
            cantidad = cantidades[id_producto]

            cursor.execute("""
                SELECT id_stock, cantidad_disponible
                FROM stock
                WHERE id_producto = %s
                ORDER BY id_stock
                FOR UPDATE
            """, (id_producto,))

            existencias = cursor.fetchall()

            disponible = sum(
                fila["cantidad_disponible"]
                for fila in existencias
            )

            if disponible < cantidad:
                raise ValueError(
                    f"Stock insuficiente para el producto #{id_producto}."
                )

            cursor.execute("""
                SELECT nombre_producto, precio
                FROM producto
                WHERE id_producto = %s
            """, (id_producto,))

            producto = cursor.fetchone()

            if not producto:
                raise ValueError("Producto no encontrado.")

            precio = Decimal(str(producto["precio"]))
            subtotal = precio * cantidad

            total += subtotal

            detalles.append({
                "id_producto": id_producto,
                "cantidad": cantidad,
                "precio": precio,
                "subtotal": subtotal,
                "existencias": existencias
            })

        cursor.execute("""
            INSERT INTO venta
            (id_cliente, id_usuario, total, metodo_pago)
            VALUES (%s, %s, %s, %s)
        """, (id_cliente, id_usuario, total, metodo_pago))

        id_venta = cursor.lastrowid

        for detalle in detalles:
            cursor.execute("""
                INSERT INTO detalle_venta
                (id_venta, id_producto, cantidad,
                 subtotal, precio_unitario)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                id_venta,
                detalle["id_producto"],
                detalle["cantidad"],
                detalle["subtotal"],
                detalle["precio"]
            ))

            restante = detalle["cantidad"]

            for fila in detalle["existencias"]:
                descontar = min(
                    restante, fila["cantidad_disponible"]
                )

                if descontar:
                    cursor.execute("""
                        UPDATE stock
                        SET cantidad_disponible =
                            cantidad_disponible - %s
                        WHERE id_stock = %s
                    """, (descontar, fila["id_stock"]))

                    restante -= descontar

                if restante == 0:
                    break

        numero_factura = (
            f"FAC-{id_venta}-{uuid4().hex[:8].upper()}"
        )

        cursor.execute("""
            INSERT INTO historial_facturas
            (id_venta, numero_factura)
            VALUES (%s, %s)
        """, (id_venta, numero_factura))

        conexion.commit()

        return {
            "id_venta": id_venta,
            "numero_factura": numero_factura
        }

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()
