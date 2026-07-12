# Verificación de endpoints del backend Django

> Nota de alcance: los tests automatizados de endpoints y CI/CD quedaron
> fuera del alcance de este proyecto. Por eso esta verificación es manual
> (vía `curl`), no una suite de pytest/unittest. Los pasos de abajo son los
> mismos que se ejecutaron para validar este módulo antes de la entrega.

## Requisito previo

Servidor corriendo (`python manage.py runserver`) y al menos un
Administrador creado. Para crear uno rápido:

```bash
python manage.py shell -c "
from apps.autenticacion.models import Usuario
Usuario.objects.create_superuser(correo='admin@litethinking.com', password='Admin12345!')
"
```

## 1. Login (obtiene access + refresh, con el rol embebido)

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"correo": "admin@litethinking.com", "password": "Admin12345!"}'
```

Guarda el valor de `access` en una variable para los siguientes pasos:

```bash
export ACCESS="<pega aquí el access token>"
```

## 2. Refrescar el access token

```bash
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh token>"}'
```

## 3. Empresas: lectura pública (rol Externo, sin token)

```bash
curl http://localhost:8000/api/empresas/
```

## 4. Empresas: escritura requiere Administrador

```bash
# Sin token: debe responder 401
curl -i -X POST http://localhost:8000/api/empresas/ \
  -H "Content-Type: application/json" \
  -d '{"nit": "900123456-7", "nombre": "Acme SAS", "direccion": "Cra 1 # 2-3", "telefono": "+573001234567"}'

# Con token: debe responder 201
curl -X POST http://localhost:8000/api/empresas/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS" \
  -d '{"nit": "900123456-7", "nombre": "Acme SAS", "direccion": "Cra 1 # 2-3", "telefono": "+573001234567"}'
```

Actualizar y eliminar:

```bash
curl -X PATCH http://localhost:8000/api/empresas/900123456-7/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS" \
  -d '{"telefono": "+573009999999"}'

curl -X DELETE http://localhost:8000/api/empresas/900123456-7/ \
  -H "Authorization: Bearer $ACCESS"
```

## 5. Productos: requiere Administrador para todo (incluida lectura)

```bash
# Sin token: debe responder 401
curl -i http://localhost:8000/api/productos/

# Crear producto con precios en varias monedas
curl -X POST http://localhost:8000/api/productos/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS" \
  -d '{
    "codigo": "PROD-001",
    "nombre": "Laptop Empresarial",
    "caracteristicas": "16GB RAM, 512GB SSD",
    "empresa": "900123456-7",
    "precios": [
      {"moneda": "COP", "valor": "4500000.00"},
      {"moneda": "USD", "valor": "1150.00"}
    ]
  }'

# Filtrar por empresa
curl "http://localhost:8000/api/productos/?empresa=900123456-7" \
  -H "Authorization: Bearer $ACCESS"
```

## 6. Validaciones esperadas (deben responder 400)

```bash
# NIT con formato inválido
curl -i -X POST http://localhost:8000/api/empresas/ \
  -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" \
  -d '{"nit": "abc", "nombre": "X", "direccion": "Y", "telefono": "123"}'

# Producto con la misma moneda repetida
curl -i -X POST http://localhost:8000/api/productos/ \
  -H "Content-Type: application/json" -H "Authorization: Bearer $ACCESS" \
  -d '{"codigo": "PROD-002", "nombre": "Mouse", "empresa": "900123456-7",
       "precios": [{"moneda": "COP", "valor": "50000"}, {"moneda": "COP", "valor": "13"}]}'
```

## Resultado de esta verificación (ejecutada durante la implementación)

| Prueba                                         | Resultado esperado | Obtenido |
|-------------------------------------------------|---------------------|----------|
| Login con credenciales válidas                  | 200 + access/refresh| ✅ |
| Refresh de token                                | 200 + nuevo access  | ✅ |
| GET Empresas sin token                          | 200 (lista)         | ✅ |
| POST Empresas sin token                         | 401                 | ✅ |
| POST Empresas con token Administrador           | 201                 | ✅ |
| PATCH / DELETE Empresas con token                | 200 / 204          | ✅ |
| GET Productos sin token                         | 401                 | ✅ |
| POST Productos con token, múltiples monedas     | 201                 | ✅ |
| Filtro de Productos por Empresa                 | 200 (filtrado)      | ✅ |
| PATCH / DELETE Productos con token               | 200 / 204          | ✅ |
| NIT inválido                                     | 400                 | ✅ |
| Moneda repetida en Producto                      | 400                 | ✅ |
