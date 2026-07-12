"""
Generación del PDF de Inventario.

Responsabilidad exclusiva de infraestructura (FastAPI): compone un
documento a partir de datos de Django (Empresa, Productos, vía
`django_client`) y de las entidades de dominio `Inventario` ya
obtenidas por `InventarioService`. El dominio no conoce reportlab ni
ningún formato de salida.
"""

from __future__ import annotations

import io
from datetime import datetime, timezone

from lite_thinking_domain.entities.inventario import Inventario
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _formatear_precios(precios: list[dict]) -> str:
    if not precios:
        return "-"
    return " / ".join(f"{p['moneda']} {float(p['valor']):,.2f}" for p in precios)


def generar_pdf_inventario(
    empresa: dict,
    productos: list[dict],
    registros: list[Inventario],
) -> bytes:
    """Devuelve los bytes de un PDF con el inventario de una empresa."""

    productos_por_codigo = {producto["codigo"]: producto for producto in productos}

    buffer = io.BytesIO()
    documento = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        title=f"Inventario - {empresa.get('nombre', '')}",
    )

    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        "TituloInventario", parent=estilos["Title"], fontSize=16, spaceAfter=4
    )
    estilo_subtitulo = ParagraphStyle(
        "SubtituloInventario", parent=estilos["Normal"], fontSize=10, textColor=colors.grey
    )

    elementos = [
        Paragraph(f"Inventario - {empresa.get('nombre', 'Empresa')}", estilo_titulo),
        Paragraph(
            f"NIT: {empresa.get('nit', '-')} · Dirección: {empresa.get('direccion', '-')} "
            f"· Teléfono: {empresa.get('telefono', '-')}",
            estilo_subtitulo,
        ),
        Paragraph(
            f"Generado el {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
            estilo_subtitulo,
        ),
        Spacer(1, 0.6 * cm),
    ]

    encabezados = ["Código", "Producto", "Cantidad", "Precio(s)"]
    filas = [encabezados]
    total_unidades = 0

    for registro in registros:
        producto = productos_por_codigo.get(registro.producto_codigo)
        nombre_producto = producto["nombre"] if producto else "(producto no encontrado)"
        precios = producto["precios"] if producto else []
        cantidad = int(registro.cantidad)
        total_unidades += cantidad
        filas.append(
            [
                registro.producto_codigo,
                nombre_producto,
                str(cantidad),
                _formatear_precios(precios),
            ]
        )

    if len(filas) == 1:
        filas.append(["-", "Sin registros de inventario", "0", "-"])

    tabla = Table(filas, colWidths=[3 * cm, 6 * cm, 2.5 * cm, 5.5 * cm], repeatRows=1)
    tabla.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0E4B45")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D8DEDB")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F6F5")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (2, 0), (2, -1), "CENTER"),
            ]
        )
    )
    elementos.append(tabla)
    elementos.append(Spacer(1, 0.5 * cm))
    elementos.append(
        Paragraph(f"Total de unidades en inventario: <b>{total_unidades}</b>", estilos["Normal"])
    )

    documento.build(elementos)
    return buffer.getvalue()
