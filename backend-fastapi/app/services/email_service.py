"""
Envío del PDF de Inventario por correo.

Responsabilidad exclusiva de FastAPI. Usa smtplib
(librería estándar) para no introducir un framework de correo nuevo.

Si `SMTP_HOST` no está configurado, se usa un modo "consola": el
correo se registra en el log del proceso en vez de enviarse de
verdad. Esto permite verificar el flujo completo (generación de PDF +
"envío") en un entorno de prueba sin credenciales SMTP reales.
"""

from __future__ import annotations

import logging
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger("inventario.correo")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(asctime)s [%(name)s] %(message)s"))
    logger.addHandler(_handler)
logger.setLevel(logging.INFO)
logger.propagate = False


def enviar_pdf_por_correo(
    destinatario: str,
    asunto: str,
    cuerpo: str,
    nombre_adjunto: str,
    contenido_pdf: bytes,
) -> str:
    """Envía (o simula) el correo. Devuelve el modo usado: 'smtp' o 'consola'."""

    mensaje = MIMEMultipart()
    mensaje["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    mensaje["To"] = destinatario
    mensaje["Subject"] = asunto
    mensaje.attach(MIMEText(cuerpo, "plain"))

    adjunto = MIMEApplication(contenido_pdf, _subtype="pdf")
    adjunto.add_header("Content-Disposition", "attachment", filename=nombre_adjunto)
    mensaje.attach(adjunto)

    if not settings.SMTP_HOST:
        logger.info(
            "MODO CONSOLA (sin SMTP_HOST configurado): correo simulado para %s | asunto: %s | adjunto: %s (%d bytes)",
            destinatario,
            asunto,
            nombre_adjunto,
            len(contenido_pdf),
        )
        return "consola"

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as servidor:
            if settings.SMTP_USE_TLS:
                servidor.starttls()
            if settings.SMTP_USER:
                servidor.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            servidor.sendmail(settings.SMTP_FROM_EMAIL, [destinatario], mensaje.as_string())
    except smtplib.SMTPAuthenticationError as exc:
        logger.error("Autenticación SMTP rechazada por %s: %s", settings.SMTP_HOST, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "El servidor SMTP rechazó las credenciales configuradas "
                "(SMTP_USER/SMTP_PASSWORD)."
            ),
        ) from exc
    except (TimeoutError, smtplib.SMTPException, OSError) as exc:
        logger.error("No se pudo enviar el correo vía %s:%s: %s", settings.SMTP_HOST, settings.SMTP_PORT, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "No se pudo conectar con el servidor SMTP configurado "
                f"({settings.SMTP_HOST}:{settings.SMTP_PORT}). Verifica SMTP_HOST, "
                "SMTP_PORT y que el puerto no esté bloqueado por la red."
            ),
        ) from exc

    return "smtp"
