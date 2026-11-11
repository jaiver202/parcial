
from database.conexion import obtener_conexion


def obtener_resumen():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        # Ventas del día
        cursor.execute("""
            SELECT
                COALESCE(SUM(total), 0) AS total,
                COUNT(*) AS cantidad
            FROM venta
            WHERE DATE(fecha_venta) = CURDATE()
        """)
        ventas_hoy = cursor.fetchone()

        # Clientes registrados
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM cliente
        """)
        clientes = cursor.fetchone()["total"]

        # Ventas del mes
        cursor.execute("""
            SELECT COALESCE(SUM(total), 0) AS total
            FROM venta
            WHERE YEAR(fecha_venta) = YEAR(CURDATE())
              AND MONTH(fecha_venta) = MONTH(CURDATE())
        """)
        ventas_mes = cursor.fetchone()["total"]

        # Productos con stock bajo
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM stock
            WHERE cantidad_disponible <= 3
        """)
        stock_bajo = cursor.fetchone()["total"]

        # Ventas recientes
        cursor.execute("""
            SELECT
                v.id_venta,
                c.nombre AS cliente,
                v.fecha_venta,
                v.total,
                h.numero_factura
            FROM venta v
            INNER JOIN cliente c
                ON v.id_cliente = c.id_cliente
            LEFT JOIN historial_facturas h
                ON v.id_venta = h.id_venta
            ORDER BY v.fecha_venta DESC, v.id_venta DESC
            LIMIT 5
        """)
        ventas_recientes = cursor.fetchall()

        # Alertas de inventario
        cursor.execute("""
            SELECT
                p.id_producto,
                p.nombre_producto,
                s.cantidad_disponible
            FROM stock s
            INNER JOIN producto p
                ON s.id_producto = p.id_producto
            WHERE s.cantidad_disponible <= 3
            ORDER BY s.cantidad_disponible ASC
        """)
        alertas = cursor.fetchall()

        return {
            "ventas_hoy": ventas_hoy,
            "clientes": clientes,
            "ventas_mes": ventas_mes,
            "stock_bajo": stock_bajo,
            "ventas_recientes": ventas_recientes,
            "alertas": alertas
        }

    finally:
        cursor.close()
        conexion.close()
