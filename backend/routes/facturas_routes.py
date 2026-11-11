
from flask import (
    Blueprint, render_template, abort, send_file
)
from datetime import datetime
from io import BytesIO
from decimal import Decimal
from xml.sax.saxutils import escape

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table,
    TableStyle, Spacer
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import cm

from utils.permisos import login_requerido
from services.facturas_service import (
    obtener_facturas,
    obtener_factura
)

facturas_bp = Blueprint(
    "facturas",
    __name__,
    url_prefix="/facturas"
)


@facturas_bp.route("/")
@login_requerido
def listar():
    return render_template(
        "facturas/listar.html",
        facturas=obtener_facturas(),
        titulo_pagina="Facturas",
        fecha_actual=datetime.now().strftime("%d/%m/%Y")
    )


@facturas_bp.route("/venta/<int:id_venta>")
@login_requerido
def detalle(id_venta):
    factura = obtener_factura(id_venta)

    if not factura:
        abort(404)

    return render_template(
        "facturas/detalle.html",
        factura=factura,
        titulo_pagina="Factura",
        fecha_actual=datetime.now().strftime("%d/%m/%Y")
    )


@facturas_bp.route("/venta/<int:id_venta>/pdf")
@login_requerido
def descargar_pdf(id_venta):
    factura = obtener_factura(id_venta)

    if not factura:
        abort(404)

    buffer = BytesIO()

    documento = SimpleDocTemplate(
        buffer,
        pagesize=(21 * cm, 29.7 * cm),
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    estilos = getSampleStyleSheet()
    estilos["Title"].textColor = colors.HexColor("#A33765")
    estilos["Title"].alignment = TA_CENTER

    contenido = []

    contenido.append(
        Paragraph("CandyKane", estilos["Title"])
    )

    contenido.append(
        Paragraph(
            "Postrería - CRM + POS",
            estilos["Normal"]
        )
    )

    contenido.append(Spacer(1, 18))

    contenido.append(
        Paragraph(
            "FACTURA DE VENTA",
            estilos["Heading2"]
        )
    )

    def campo(valor):
        return escape(str(valor if valor is not None else ""))

    fecha = factura["fecha_emision"].strftime("%d/%m/%Y")

    informacion = [
        ("Factura:", factura["numero_factura"]),
        ("Fecha:", fecha),
        ("Cliente:", factura["cliente"]),
        ("Teléfono:", factura["telefono"] or "No registrado"),
        ("Vendedor:", factura["vendedor"]),
        ("Método de pago:", factura["metodo_pago"] or "No registrado")
    ]

    for etiqueta, valor in informacion:
        contenido.append(
            Paragraph(
                f"<b>{campo(etiqueta)}</b> {campo(valor)}",
                estilos["Normal"]
            )
        )
        contenido.append(Spacer(1, 5))

    contenido.append(Spacer(1, 16))

    datos = [[
        "Producto", "Cantidad", "Precio", "Subtotal"
    ]]

    for producto in factura["detalles"]:
        datos.append([
            Paragraph(
                campo(producto["nombre_producto"]),
                estilos["Normal"]
            ),
            str(producto["cantidad"]),
            f'$ {Decimal(str(producto["precio_unitario"])):,.2f}',
            f'$ {Decimal(str(producto["subtotal"])):,.2f}'
        ])

    tabla = Table(
        datos,
        colWidths=[7 * cm, 2.5 * cm, 3.5 * cm, 4 * cm],
        repeatRows=1,
        hAlign="LEFT"
    )

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0),
         colors.HexColor("#F8E8EF")),
        ("TEXTCOLOR", (0, 0), (-1, 0),
         colors.HexColor("#A33765")),
        ("GRID", (0, 0), (-1, -1),
         0.3, colors.HexColor("#EAD7DF")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10)
    ]))

    contenido.append(tabla)
    contenido.append(Spacer(1, 20))

    contenido.append(
        Paragraph(
            f'<b>Total: $ {Decimal(str(factura["total"])):,.2f}</b>',
            estilos["Heading2"]
        )
    )

    contenido.append(Spacer(1, 25))

    contenido.append(
        Paragraph(
            "Gracias por endulzar tu día con nosotros.",
            estilos["Normal"]
        )
    )

    documento.build(contenido)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=False,
        download_name=f'Factura-{id_venta}.pdf',
        mimetype="application/pdf"
    )
