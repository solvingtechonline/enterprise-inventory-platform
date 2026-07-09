# lite-thinking-domain

Paquete de dominio desacoplado (Arquitectura Limpia) para la prueba técnica
Lite Thinking 2026.

## Reglas

- **Cero dependencias** de Django, FastAPI, HTTP o cualquier framework web.
- Consumido como dependencia instalada por `backend-django` y `backend-fastapi`.
- Contiene entidades, objetos de valor, interfaces de repositorio y servicios
  de dominio puro.

## Estructura

```
src/lite_thinking_domain/
├── entities/        # Entidades de negocio (Empresa, Producto, Inventario...)
├── value_objects/   # Objetos de valor (dinero multi-moneda, etc.)
├── repositories/     # Interfaces (puertos) de persistencia, sin implementación
└── services/         # Reglas de negocio / casos de uso puros
```

## Instalación y verificación aislada

```bash
cd domain
poetry install
poetry run pytest
```

## Consumo desde Django o FastAPI

Cada backend agrega este paquete como dependencia local en su propio
`pyproject.toml` / `requirements.txt`, por ejemplo:

```toml
lite-thinking-domain = { path = "../domain", develop = true }
```
