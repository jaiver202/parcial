import bcrypt
from database.conexion import obtener_conexion


def autenticar_usuario(email, contrasena):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id_usuario, nombre_usuario,
                   email, contrasena, rol, estado
            FROM usuarios
            WHERE email = %s
            LIMIT 1
            """,
            (email,)
        )

        usuario = cursor.fetchone()

        if not usuario:
            return None

        if usuario["estado"] != "activo":
            return None

        hash_guardado = usuario["contrasena"].encode("utf-8")

        if not bcrypt.checkpw(
            contrasena.encode("utf-8"),
            hash_guardado
        ):
            return None

        usuario.pop("contrasena")

        return usuario

    finally:
        cursor.close()
        conexion.close()