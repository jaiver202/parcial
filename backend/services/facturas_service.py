
from database.conexion import obtener_conexion


def obtener_facturas():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                f.id_factura,
                f.id_venta,
                f.numero_factura,
                f.fecha_emision,
                v.total,
                v.metodo_pago,
                c.nombre AS cliente,
                c.telefono,
                u.nombre_usuario AS vendedor
            FROM historial_facturas f
            INNER JOIN venta v
                ON f.id_venta = v.id_venta
            INNER JOIN cliente c
                ON v.id_cliente = c.id_cliente
            INNER JOIN usuarios u
                ON v.id_usuario = u.id_usuario
            ORDER BY f.fecha_emision DESC, f.id_factura DESC
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        conexion.close()


def obtener_factura(id_venta):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                f.id_factura,
                f.numero_factura,
                f.fecha_emision,
                v.id_venta,
                v.fecha_venta,
                v.total,
                v.metodo_pago,
                c.nombre AS cliente,
                c.email,
                c.telefono,
                c.direccion,
                c.ciudad,
                c.pais,
                u.nombre_usuario AS vendedor
            FROM historial_facturas f
            INNER JOIN venta v
                ON f.id_venta = v.id_venta
            INNER JOIN cliente c
                ON v.id_cliente = c.id_cliente
            INNER JOIN usuarios u
                ON v.id_usuario = u.id_usuario
            WHERE v.id_venta = %s
        """, (id_venta,))

        factura = cursor.fetchone()

        if not factura:
            return None

        cursor.execute("""
            SELECT
                p.nombre_producto,
                d.cantidad,
                d.subtotal,
                COALESCE(
                    d.precio_unitario,
                    d.subtotal / NULLIF(d.cantidad, 0)
                ) AS precio_unitario
            FROM detalle_venta d
            INNER JOIN producto p
                ON d.id_producto = p.id_producto
            WHERE d.id_venta = %s
            ORDER BY d.id_detalle
        """, (id_venta,))

        factura["detalles"] = cursor.fetchall()

        return factura

    finally:
        cursor.close()
        conexion.close()
