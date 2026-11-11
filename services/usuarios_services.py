
import os
import bcrypt
import mysql.connector
from mysql.connector import IntegrityError
from dotenv import load_dotenv

load_dotenv()


def conexion():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "canbase")
    )


def listar_usuarios():
    cn = conexion()
    cursor = cn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT id_usuario, nombre_usuario,
                   email, rol, estado
            FROM usuarios
            ORDER BY id_usuario DESC
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        cn.close()


def obtener_usuario(id_usuario):
    cn = conexion()
    cursor = cn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT id_usuario, nombre_usuario,
                   email, rol, estado
            FROM usuarios
            WHERE id_usuario = %s
        """, (id_usuario,))
        return cursor.fetchone()
    finally:
        cursor.close()
        cn.close()


def hash_password(contrasena):
    return bcrypt.hashpw(
        contrasena.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def crear_usuario(nombre, email, contrasena, rol, estado):
    cn = conexion()
    cursor = cn.cursor()

    try:
        cursor.execute("""
            INSERT INTO usuarios
                (nombre_usuario, email, contrasena, rol, estado)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            nombre,
            email,
            hash_password(contrasena),
            rol,
            estado
        ))
        cn.commit()
    except Exception:
        cn.rollback()
        raise
    finally:
        cursor.close()
        cn.close()


def actualizar_usuario(
    id_usuario, nombre, email,
    rol, estado, contrasena=None
):
    cn = conexion()
    cursor = cn.cursor()

    try:
        if contrasena:
            cursor.execute("""
                UPDATE usuarios
                SET nombre_usuario = %s,
                    email = %s,
                    rol = %s,
                    estado = %s,
                    contrasena = %s
                WHERE id_usuario = %s
            """, (
                nombre, email, rol, estado,
                hash_password(contrasena),
                id_usuario
            ))
        else:
            cursor.execute("""
                UPDATE usuarios
                SET nombre_usuario = %s,
                    email = %s,
                    rol = %s,
                    estado = %s
                WHERE id_usuario = %s
            """, (
                nombre, email, rol, estado,
                id_usuario
            ))

        if cursor.rowcount == 0:
            raise ValueError("Usuario no encontrado o sin cambios.")

        cn.commit()
    except Exception:
        cn.rollback()
        raise
    finally:
        cursor.close()
        cn.close()


def eliminar_usuario(id_usuario):
    cn = conexion()
    cursor = cn.cursor()

    try:
        cursor.execute(
            "DELETE FROM usuarios WHERE id_usuario = %s",
            (id_usuario,)
        )
        cn.commit()
    except Exception:
        cn.rollback()
        raise
    finally:
        cursor.close()
        cn.close()
