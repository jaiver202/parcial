
from database.conexion import obtener_conexion

def listar_clientes(busqueda=""):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        sql = """
            SELECT id_cliente, nombre, email, telefono,
                   direccion, ciudad, pais, fecha_registro
            FROM cliente
        """
        parametros = ()

        if busqueda:
            sql += """
                WHERE nombre LIKE %s
                   OR email LIKE %s
                   OR telefono LIKE %s
                   OR ciudad LIKE %s
            """
            patron = f"%{busqueda}%"
            parametros = (patron,) * 4

        sql += " ORDER BY id_cliente DESC"

        cursor.execute(sql, parametros)
        return cursor.fetchall()

    finally:
        cursor.close()
        conexion.close()


def obtener_cliente(id_cliente):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM cliente WHERE id_cliente = %s",
            (id_cliente,)
        )
        return cursor.fetchone()

    finally:
        cursor.close()
        conexion.close()


def crear_cliente(datos):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("""
            INSERT INTO cliente
            (nombre, email, telefono, direccion, ciudad, pais)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            datos["nombre"],
            datos["email"],
            datos["telefono"],
            datos["direccion"],
            datos["ciudad"],
            datos["pais"]
        ))

        conexion.commit()
        return cursor.lastrowid

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()


def actualizar_cliente(id_cliente, datos):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("""
            UPDATE cliente
            SET nombre = %s,
                email = %s,
                telefono = %s,
                direccion = %s,
                ciudad = %s,
                pais = %s
            WHERE id_cliente = %s
        """, (
            datos["nombre"],
            datos["email"],
            datos["telefono"],
            datos["direccion"],
            datos["ciudad"],
            datos["pais"],
            id_cliente
        ))

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()


def eliminar_cliente(id_cliente):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute(
            "DELETE FROM cliente WHERE id_cliente = %s",
            (id_cliente,)
        )
        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()
