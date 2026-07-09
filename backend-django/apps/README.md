# apps/

Apps funcionales de Django:

- `apps/autenticacion` — Modelo Usuario (Administrador), login con
  correo/contraseña, emisión de token JWT con el claim `rol`, permisos
  compartidos por rol (`EsAdministrador`, `LecturaLibreEscrituraAdministrador`).
- `apps/empresas` — CRUD de Empresa. Lectura pública (Externo, sin auth),
  escritura solo Administrador.
- `apps/productos` — CRUD de Producto asociado a Empresa, con precios en
  varias monedas. Requiere rol Administrador para todas las operaciones
  (supuesto documentado: ver `apps/productos/views.py`).

Nota: el Inventario no vive aquí; se gestiona en el microservicio FastAPI
(`backend-fastapi/`), que es su dueño exclusivo.
