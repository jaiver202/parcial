import bcrypt
from database.conexion import obtener_conexion

nombre = "jaiver"
email = "admin@candykane.com"
contrasena = input("Contraseña del administrador: ")

if len(contrasena) < 8:
    raise ValueError("La contraseña debe tener al menos 8 caracteres")

hash_contrasena = bcrypt.hashpw(
    contrasena.encode("utf-8"),
    bcrypt.gensalt()
).decode("utf-8")

conexion = obtener_conexion()
cursor = conexion.cursor()

try:
    cursor.execute(
        """
        INSERT INTO usuarios
        (nombre_usuario, email, contrasena, rol, estado)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (nombre, email, hash_contrasena, "administrador", "activo")
    )
    conexion.commit()
    print("Administrador creado correctamente")
except Exception:
    conexion.rollback()
    raise
finally:
    cursor.close()
    conexion.close()