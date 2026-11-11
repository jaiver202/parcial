
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, session, send_file
)

from datetime import datetime
from io import BytesIO
from xml.sax.saxutils import escape

from mysql.connector import IntegrityError

# LIBRERÍAS PARA GENERAR PDF
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    TableStyle,
    Spacer
)

from reportlab.lib import colors
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

# PERMISOS
from utils.permisos import login_requerido

# SERVICIOS DE CLIENTES
from services.clientes_service import (
    listar_clientes,
    obtener_cliente,
    crear_cliente,
    actualizar_cliente,
    eliminar_cliente
)

# SERVICIO DEL REPORTE POR NACIONALIDAD
from services.reportes_servicios import (
    obtener_reporte_nacionalidad
)


# ==========================================
# BLUEPRINT DE CLIENTES
# ==========================================

clientes_bp = Blueprint(
    "clientes",
    __name__,
    url_prefix="/clientes"
)


# ==========================================
# LEER DATOS DEL FORMULARIO
# ==========================================

def leer_formulario():
    return {
        "nombre": request.form.get("nombre", "").strip(),
        "email": request.form.get("email", "").strip() or None,
        "telefono": request.form.get("telefono", "").strip() or None,
        "direccion": request.form.get("direccion", "").strip() or None,
        "ciudad": request.form.get("ciudad", "").strip() or None,
        "pais": request.form.get("pais", "").strip()
    }


# ==========================================
# VALIDAR DATOS DEL CLIENTE
# ==========================================

def datos_validos(datos):
    return (
        bool(datos["nombre"])
        and bool(datos["pais"])
        and len(datos["nombre"]) <= 100
        and len(datos["pais"]) <= 50
        and (datos["email"] is None or len(datos["email"]) <= 100)
        and (datos["telefono"] is None or len(datos["telefono"]) <= 20)
        and (datos["ciudad"] is None or len(datos["ciudad"]) <= 50)
        and (datos["direccion"] is None or len(datos["direccion"]) <= 150)
    )


# ==========================================
# LISTAR CLIENTES Y MOSTRAR REPORTE
# ==========================================

@clientes_bp.route("/")
@login_requerido
def listar():

    # Obtener búsqueda
    busqueda = request.args.get("buscar", "").strip()

    # Obtener clientes registrados
    clientes = listar_clientes(busqueda)

    # Obtener clasificación por nacionalidad
    reporte, total_reporte = obtener_reporte_nacionalidad()

    # Mostrar página de clientes
    return render_template(
        "clientes/listar.html",
        clientes=clientes,
        busqueda=busqueda,
        reporte=reporte,
        total_reporte=total_reporte,
        fecha_actual=datetime.now().strftime("%d/%m/%Y"),
        titulo_pagina="Clientes"
    )


# ==========================================
# CREAR CLIENTE
# ==========================================

@clientes_bp.route("/crear", methods=["POST"])
@login_requerido
def crear():

    datos = leer_formulario()

    if not datos_validos(datos):
        flash(
            "Verifica los datos obligatorios y su longitud.",
            "danger"
        )
        return redirect(url_for("clientes.listar"))

    crear_cliente(datos)

    flash(
        "Cliente registrado correctamente.",
        "success"
    )

    return redirect(url_for("clientes.listar"))


# ==========================================
# EDITAR CLIENTE
# ==========================================

@clientes_bp.route("/editar/<int:id_cliente>", methods=["POST"])
@login_requerido
def editar(id_cliente):

    datos = leer_formulario()

    if not datos_validos(datos):
        flash(
            "Verifica los datos del cliente.",
            "danger"
        )
        return redirect(url_for("clientes.listar"))

    if not obtener_cliente(id_cliente):
        flash(
            "El cliente no existe.",
            "warning"
        )
        return redirect(url_for("clientes.listar"))

    actualizar_cliente(id_cliente, datos)

    flash(
        "Cliente actualizado correctamente.",
        "success"
    )

    return redirect(url_for("clientes.listar"))


# ==========================================
# ELIMINAR CLIENTE
# ==========================================

@clientes_bp.route("/eliminar/<int:id_cliente>", methods=["POST"])
@login_requerido
def eliminar(id_cliente):

    if not obtener_cliente(id_cliente):
        flash(
            "El cliente no existe.",
            "warning"
        )
        return redirect(url_for("clientes.listar"))

    try:
        eliminar_cliente(id_cliente)

        flash(
            "Cliente eliminado correctamente.",
            "success"
        )

    except IntegrityError:
        flash(
            "No puedes eliminar este cliente porque tiene ventas asociadas.",
            "danger"
        )

    return redirect(url_for("clientes.listar"))


# ==========================================
# GENERAR PDF DEL REPORTE POR NACIONALIDAD
# ==========================================

@clientes_bp.route("/reporte/nacionalidad/pdf")
@login_requerido
def reporte_nacionalidad_pdf():

    # Obtener datos reales de MySQL
    reporte, total = obtener_reporte_nacionalidad()

    # Crear PDF en memoria
    buffer = BytesIO()

    documento = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=28 * mm,
        bottomMargin=20 * mm
    )

    # ======================================
    # ESTILOS DEL DOCUMENTO
    # ======================================

    estilos = getSampleStyleSheet()

    estilos.add(ParagraphStyle(
        name="MarcaKane",
        fontName="Times-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#AD3768")
    ))

    estilos.add(ParagraphStyle(
        name="TituloKane",
        fontName="Times-Bold",
        fontSize=17,
        leading=22,
        textColor=colors.HexColor("#301321"),
        spaceAfter=14
    ))

    estilos.add(ParagraphStyle(
        name="TextoKane",
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#977A88")
    ))

    fecha = datetime.now().strftime("%d/%m/%Y")

    # ======================================
    # ENCABEZADO DEL REPORTE
    # ======================================

    encabezado = Table([
        [
            [
                Paragraph(
                    "CandyKane",
                    estilos["MarcaKane"]
                ),
                Paragraph(
                    "Reporte CRM de clientes",
                    estilos["TextoKane"]
                )
            ],
            Paragraph(
                fecha,
                estilos["TextoKane"]
            )
        ]
    ], colWidths=[125 * mm, 49 * mm])

    encabezado.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        (
            "LINEBELOW",
            (0, 0),
            (-1, -1),
            0.6,
            colors.HexColor("#EBD9E0")
        )
    ]))

    # ======================================
    # DATOS DE LA TABLA
    # ======================================

    datos = [[
        "NACIONALIDAD",
        "CLIENTES",
        "PARTICIPACIÓN"
    ]]

    for fila in reporte:

        datos.append([
            Paragraph(
                escape(str(fila["nacionalidad"])),
                estilos["TextoKane"]
            ),
            str(fila["cantidad"]),
            f'{fila["porcentaje"]:g}%'
        ])

    # Total general
    datos.append([
        "Total general",
        str(total),
        "100%" if total else "0%"
    ])

    # ======================================
    # CREAR TABLA DEL PDF
    # ======================================

    tabla = Table(
        datos,
        colWidths=[
            85 * mm,
            38 * mm,
            51 * mm
        ],
        repeatRows=1
    )

    tabla.setStyle(TableStyle([

        # Encabezado rosado
        (
            "BACKGROUND",
            (0, 0),
            (-1, 0),
            colors.HexColor("#F8E8EE")
        ),

        # Texto del encabezado
        (
            "TEXTCOLOR",
            (0, 0),
            (-1, 0),
            colors.HexColor("#AD3768")
        ),

        # Fuente del encabezado
        (
            "FONTNAME",
            (0, 0),
            (-1, 0),
            "Helvetica-Bold"
        ),

        # Fuente de los registros
        (
            "FONTNAME",
            (0, 1),
            (-1, -2),
            "Helvetica"
        ),

        # Total general en negrita
        (
            "FONTNAME",
            (0, -1),
            (-1, -1),
            "Helvetica-Bold"
        ),

        # Tamaño de texto
        (
            "FONTSIZE",
            (0, 0),
            (-1, -1),
            9
        ),

        # Espaciado
        (
            "TOPPADDING",
            (0, 0),
            (-1, -1),
            10
        ),

        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, -1),
            10
        ),

        (
            "LEFTPADDING",
            (0, 0),
            (-1, -1),
            9
        ),

        # Líneas divisorias
        (
            "LINEBELOW",
            (0, 1),
            (-1, -1),
            0.5,
            colors.HexColor("#EBD9E0")
        ),

        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "MIDDLE"
        ),

        # Alinear cantidades
        (
            "ALIGN",
            (1, 1),
            (-1, -1),
            "CENTER"
        )

    ]))

    # CONTENIDO FINAL DEL PDF
    elementos = [
        encabezado,
        Spacer(1, 18),
        Paragraph(
            "Clasificación por nacionalidad",
            estilos["TituloKane"]
        ),
        tabla
    ]

    # Generar PDF
    documento.build(elementos)

    buffer.seek(0)


    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=False,
        download_name="reporte_nacionalidad.pdf"
    )
