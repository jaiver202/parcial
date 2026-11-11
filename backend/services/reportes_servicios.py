
from database.conexion import obtener_conexion


# ==========================================
# REPORTE DE CLIENTES POR NACIONALIDAD
# ==========================================

def obtener_reporte_nacionalidad():

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        # Consultar clientes agrupados por país
        cursor.execute("""
            SELECT
                pais AS nacionalidad,
                COUNT(*) AS cantidad
            FROM cliente
            GROUP BY pais
            ORDER BY cantidad DESC, pais ASC
        """)

        filas = cursor.fetchall()

        # Calcular total de clientes
        total = sum(fila["cantidad"] for fila in filas)

        reporte = []

        # Calcular participación por nacionalidad
        for fila in filas:

            cantidad = fila["cantidad"]

            porcentaje = (
                round((cantidad / total) * 100, 2)
                if total > 0 else 0
            )

            reporte.append({
                "nacionalidad": fila["nacionalidad"],
                "cantidad": cantidad,
                "porcentaje": porcentaje
            })

        return reporte, total

    finally:
        cursor.close()
        conexion.close()
