"""
Endpoints REST de Inventario.

FastAPI es dueño exclusivo de esta tabla, incluidos el PDF
y el envío por correo. Los endpoints de
reporte reutilizan el token del Administrador para leer Empresa y
Productos desde la API de Django (`app.services.django_client`),
delegan la composición del PDF a `app.services.pdf_service` y el envío
a `app.services.email_service`. El dominio (`InventarioService`) solo
provee los registros de Inventario; no conoce PDF ni correo.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from lite_thinking_domain.entities.inventario import Inventario
from lite_thinking_domain.services.inventario_service import InventarioService

from app.api.deps import obtener_inventario_service, requerir_administrador
from app.core.security import UsuarioToken
from app.schemas.inventario import (
    InventarioActualizarCantidad,
    InventarioRead,
    InventarioRegistrar,
    ReporteEnviarInput,
    ReporteEnviarRead,
)
from app.services import django_client, email_service, pdf_service

router = APIRouter(
    prefix="/api/inventario",
    tags=["inventario"],
    dependencies=[Depends(requerir_administrador)],
)


def _a_schema(inventario: Inventario) -> InventarioRead:
    return InventarioRead(
        id=inventario.id,
        empresa_nit=inventario.empresa_nit,
        producto_codigo=inventario.producto_codigo,
        cantidad=int(inventario.cantidad),
        actualizado_en=inventario.actualizado_en,
    )


def _construir_pdf(
    empresa_nit: str,
    usuario: UsuarioToken,
    servicio: InventarioService,
) -> tuple[bytes, dict]:
    """Compone el PDF de inventario: datos de Django + registros del dominio."""
    empresa = django_client.obtener_empresa(empresa_nit, usuario.token)
    productos = django_client.obtener_productos_por_empresa(empresa_nit, usuario.token)
    registros = servicio.listar_por_empresa(empresa_nit)
    contenido = pdf_service.generar_pdf_inventario(empresa, productos, registros)
    return contenido, empresa


@router.post(
    "/",
    response_model=InventarioRead,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar (o incrementar) stock de un producto en el inventario de una empresa",
)
def registrar_inventario(
    body: InventarioRegistrar,
    servicio: InventarioService = Depends(obtener_inventario_service),
) -> InventarioRead:
    try:
        registro = servicio.registrar_producto(
            empresa_nit=body.empresa_nit,
            producto_codigo=body.producto_codigo,
            cantidad=body.cantidad,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _a_schema(registro)


@router.get(
    "/",
    response_model=list[InventarioRead],
    summary="Listar el inventario de una empresa",
)
def listar_inventario(
    empresa_nit: str = Query(..., description="NIT de la empresa a consultar."),
    servicio: InventarioService = Depends(obtener_inventario_service),
) -> list[InventarioRead]:
    registros = servicio.listar_por_empresa(empresa_nit)
    return [_a_schema(r) for r in registros]


@router.get(
    "/reporte/pdf",
    summary="Descargar el PDF de inventario de una empresa",
    response_class=Response,
    responses={200: {"content": {"application/pdf": {}}}},
)
def descargar_reporte_pdf(
    empresa_nit: str = Query(..., description="NIT de la empresa a reportar."),
    usuario: UsuarioToken = Depends(requerir_administrador),
    servicio: InventarioService = Depends(obtener_inventario_service),
) -> Response:
    contenido, empresa = _construir_pdf(empresa_nit, usuario, servicio)
    nombre_archivo = f"inventario_{empresa.get('nit', empresa_nit)}.pdf"
    return Response(
        content=contenido,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nombre_archivo}"'},
    )


@router.post(
    "/reporte/enviar",
    response_model=ReporteEnviarRead,
    summary="Enviar por correo el PDF de inventario de una empresa",
)
def enviar_reporte_por_correo(
    body: ReporteEnviarInput,
    usuario: UsuarioToken = Depends(requerir_administrador),
    servicio: InventarioService = Depends(obtener_inventario_service),
) -> ReporteEnviarRead:
    contenido, empresa = _construir_pdf(body.empresa_nit, usuario, servicio)
    nombre_archivo = f"inventario_{empresa.get('nit', body.empresa_nit)}.pdf"
    nombre_empresa = empresa.get("nombre", body.empresa_nit)

    modo = email_service.enviar_pdf_por_correo(
        destinatario=body.destinatario,
        asunto=f"Inventario de {nombre_empresa}",
        cuerpo=(
            f"Adjunto encontrarás el PDF con el inventario actual de {nombre_empresa} "
            f"(NIT {empresa.get('nit', body.empresa_nit)})."
        ),
        nombre_adjunto=nombre_archivo,
        contenido_pdf=contenido,
    )

    mensaje = (
        f"Correo enviado a {body.destinatario}."
        if modo == "smtp"
        else f"SMTP no configurado: el envío a {body.destinatario} se simuló en modo consola."
    )
    return ReporteEnviarRead(mensaje=mensaje, modo=modo)


@router.get(
    "/{inventario_id}",
    response_model=InventarioRead,
    summary="Obtener un registro de inventario por id",
)
def obtener_inventario(
    inventario_id: int,
    servicio: InventarioService = Depends(obtener_inventario_service),
) -> InventarioRead:
    registro = servicio.obtener_por_id(inventario_id)
    if registro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe el registro de inventario id={inventario_id}.",
        )
    return _a_schema(registro)


@router.patch(
    "/{inventario_id}",
    response_model=InventarioRead,
    summary="Corregir la cantidad absoluta de un registro de inventario",
)
def actualizar_cantidad(
    inventario_id: int,
    body: InventarioActualizarCantidad,
    servicio: InventarioService = Depends(obtener_inventario_service),
) -> InventarioRead:
    try:
        registro = servicio.actualizar_cantidad(inventario_id, body.cantidad)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _a_schema(registro)


@router.delete(
    "/{inventario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un registro de inventario",
)
def eliminar_inventario(
    inventario_id: int,
    servicio: InventarioService = Depends(obtener_inventario_service),
) -> None:
    eliminado = servicio.eliminar(inventario_id)
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe el registro de inventario id={inventario_id}.",
        )
