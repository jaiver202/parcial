
from database.conexion import obtener_conexion


# ==========================================
# REPONER INVENTARIO DE UN PRODUCTO
# ==========================================

def reponer_stock(id_producto, cantidad):

    if cantidad <= 0:
        raise ValueError(
            "La cantidad debe ser mayor que cero."
        )

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        # Obtener el producto
        cursor.execute("""
            SELECT id_producto, nombre_producto
            FROM producto
            WHERE id_producto = %s
        """, (id_producto,))

        producto = cursor.fetchone()

        if not producto:
            raise ValueError("El producto no existe.")

        # Consultar y bloquear los registros de stock
        cursor.execute("""
            SELECT id_stock, cantidad_disponible
            FROM stock
            WHERE id_producto = %s
            ORDER BY id_stock
            FOR UPDATE
        """, (id_producto,))

        registros = cursor.fetchall()

        if len(registros) > 1:
            raise ValueError(
                "El producto tiene varios registros de stock. "
                "Es necesario revisarlos antes de reponer."
            )

        if registros:
            # Actualizar stock existente
            registro = registros[0]

            nuevo_stock = (
                registro["cantidad_disponible"] + cantidad
            )

            cursor.execute("""
                UPDATE stock
                SET cantidad_disponible = %s
                WHERE id_stock = %s
            """, (
                nuevo_stock,
                registro["id_stock"]
            ))

        else:
            # Crear registro si no existe
            nuevo_stock = cantidad

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

        return {
            "nombre": producto["nombre_producto"],
            "stock_nuevo": nuevo_stock
        }

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()
