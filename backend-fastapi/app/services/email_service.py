"""
Envío del PDF de Inventario por correo, vía la API HTTP de Brevo
(antes Sendinblue), invocada con `curl`.

Responsabilidad exclusiva de FastAPI, igual que antes con SMTP.

Por qué cURL contra la API HTTP de Brevo, y no SMTP: en el plan
gratuito de Render las conexiones salientes por los puertos SMTP
(25/587/465) fallan o quedan bloqueadas, mientras que la API de Brevo
viaja por HTTPS (443) como cualquier otra llamada REST del proyecto, sin
ese inconveniente. Se invoca el binario `curl` (disponible por defecto
en la imagen de Render) en vez de un cliente HTTP en Python porque es
exactamente el comando ya verificado manualmente contra la API de
Brevo; el cuerpo JSON (incluido el PDF adjunto en base64) se pasa por
stdin (`--data-binary @-`) en vez de como argumento de línea de
comandos, para no toparse con el límite de tamaño de los argumentos del
proceso ni dejar el adjunto expuesto en la lista de procesos.

Si `BREVO_API_KEY` no está configurada, se usa un modo "consola" (mismo
criterio que el modo SMTP anterior): el correo se registra en el log
del proceso en vez de enviarse de verdad. Esto permite verificar el
flujo completo (generación de PDF + "envío") en un entorno de prueba
sin credenciales reales.
"""

from __future__ import annotations

import base64
import json
import logging
import subprocess

from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger("inventario.correo")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(asctime)s [%(name)s] %(message)s"))
    logger.addHandler(_handler)
logger.setLevel(logging.INFO)
logger.propagate = False

_BREVO_ENDPOINT = "https://api.brevo.com/v3/smtp/email"
_TIMEOUT_SEGUNDOS = 15


def enviar_pdf_por_correo(
    destinatario: str,
    asunto: str,
    cuerpo: str,
    nombre_adjunto: str,
    contenido_pdf: bytes,
) -> str:
    """Envía (o simula) el correo. Devuelve el modo usado: 'brevo' o 'consola'."""

    if not settings.BREVO_API_KEY:
        logger.info(
            "MODO CONSOLA (sin BREVO_API_KEY configurada): correo simulado para %s | asunto: %s | adjunto: %s (%d bytes)",
            destinatario,
            asunto,
            nombre_adjunto,
            len(contenido_pdf),
        )
        return "consola"

    cuerpo_peticion = {
        "sender": {"name": settings.BREVO_FROM_NAME, "email": settings.BREVO_FROM_EMAIL},
        "to": [{"email": destinatario}],
        "subject": asunto,
        "textContent": cuerpo,
        "attachment": [
            {
                "content": base64.b64encode(contenido_pdf).decode("ascii"),
                "name": nombre_adjunto,
            }
        ],
    }

    try:
        resultado = subprocess.run(
            [
                "curl",
                "-sS",
                "-X",
                "POST",
                _BREVO_ENDPOINT,
                "-H",
                "accept: application/json",
                "-H",
                "content-type: application/json",
                "-H",
                f"api-key: {settings.BREVO_API_KEY}",
                "--data-binary",
                "@-",
                "--max-time",
                str(_TIMEOUT_SEGUNDOS),
                "-w",
                "\n%{http_code}",
            ],
            input=json.dumps(cuerpo_peticion).encode("utf-8"),
            capture_output=True,
            timeout=_TIMEOUT_SEGUNDOS + 5,
        )
    except FileNotFoundError as exc:
        logger.error("El binario 'curl' no está disponible en este entorno: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="El servidor no tiene 'curl' instalado, requerido para enviar el correo vía la API de Brevo.",
        ) from exc
    except subprocess.TimeoutExpired as exc:
        logger.error("Timeout llamando a la API de Brevo con curl: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="La API de Brevo no respondió a tiempo.",
        ) from exc

    salida = resultado.stdout.decode("utf-8", errors="replace")
    *cuerpo_lineas, codigo_http = salida.rsplit("\n", 1) if "\n" in salida else ("", salida)
    cuerpo_respuesta = "\n".join(cuerpo_lineas) if cuerpo_lineas else ""

    if resultado.returncode != 0:
        # Error a nivel de proceso de curl (DNS, red inalcanzable, TLS, etc.),
        # no una respuesta HTTP de Brevo — el detalle vive en stderr.
        detalle_error = resultado.stderr.decode("utf-8", errors="replace").strip()
        logger.error(
            "curl falló al llamar a la API de Brevo (código de salida %s): %s",
            resultado.returncode,
            detalle_error,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "No se pudo conectar con la API de Brevo. Verifica conectividad "
                f"saliente hacia {_BREVO_ENDPOINT} y que 'curl' funcione en este entorno."
            ),
        ) from None

    try:
        codigo_http_int = int(codigo_http.strip())
    except ValueError:
        codigo_http_int = 0

    if codigo_http_int < 200 or codigo_http_int >= 300:
        logger.error(
            "La API de Brevo respondió %s al intentar enviar el correo a %s: %s",
            codigo_http_int,
            destinatario,
            cuerpo_respuesta,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Brevo rechazó el envío del correo (HTTP {codigo_http_int}): {cuerpo_respuesta}",
        )

    return "brevo"
