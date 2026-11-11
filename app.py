
from flask import Flask, redirect, url_for
from flask_wtf.csrf import CSRFProtect
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

from routes.auth_routes import auth_bp
from routes.clientes_routes import clientes_bp
from routes.ventas_routes import ventas_bp
from routes.facturas_routes import facturas_bp
from routes.usuarios_routes import usuarios_bp

import os

# Rutas del proyecto
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"

# Cargar variables de entorno
load_dotenv(BASE_DIR / ".env")

# Crear aplicación Flask
app = Flask(
    __name__,
    template_folder=str(FRONTEND_DIR / "templates"),
    static_folder=str(FRONTEND_DIR / "static")
)

# Configuración de seguridad
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=2)

# PROTECCIÓN CSRF - AQUÍ VA
csrf = CSRFProtect(app)

# Registrar Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(clientes_bp)
app.register_blueprint(ventas_bp)
app.register_blueprint(facturas_bp)
app.register_blueprint(usuarios_bp)

@app.route("/")
def inicio():
    return redirect(url_for("auth.login"))


if __name__ == "__main__":
    app.run(debug=True, port=5001)
