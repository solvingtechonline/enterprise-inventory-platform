# Indicadores de rendimiento y calidad

Este documento recoge la evidencia real generada para verificar la calidad
del proyecto (análisis estático de código equivalente a SonarQube,
Lighthouse y GTmetrix).

Todos los resultados de este documento se generaron ejecutando las
herramientas contra el código real del proyecto o contra su despliegue
público real en Vercel (`https://enterprise-inventory-platform-beige.vercel.app/`),
sin estimar ni inventar ningún puntaje.

---

## 1. Análisis estático de calidad de código (equivalente a SonarQube)

### 1.1 Herramienta y alcance

Se usó **ruff 0.15.20** como analizador estático para los tres paquetes
Python del proyecto (`domain`, `backend-django`, `backend-fastapi`). Ruff
reimplementa, en un solo binario, las reglas de **Pyflakes** (errores reales:
imports no usados, variables no usadas, código muerto), **pycodestyle**
(estilo, PEP 8), **flake8-bugbear**, **pyupgrade**, **flake8-simplify** y
**pep8-naming**, entre otras. Es el equivalente directo, para este stack, a lo
que SonarQube evalúa en su perfil "Sonar way" para Python (bugs, code smells,
convenciones), sin requerir un servidor SonarQube propio.

Se declara como **dependencia de desarrollo únicamente**, en
`requirements-dev.txt` en la raíz del repo. **No** se agregó a
`backend-django/requirements.txt` ni a `backend-fastapi/requirements.txt`, ni
al `pyproject.toml` de producción del dominio (solo como referencia en este
documento y en el comando reproducible de más abajo).

Comando ejecutado (idéntico para los tres paquetes, ejecutado por separado):

```bash
pip install -r requirements-dev.txt
ruff check domain/src domain/tests backend-django backend-fastapi \
    --exclude "*/migrations/*" \
    --select E,F,W,I,B,C90,UP,SIM,N
```

### 1.2 Resultado inicial (antes de correcciones)

| Paquete | Hallazgos iniciales |
|---|---|
| `domain/` | 23 |
| `backend-django/` | 16 |
| `backend-fastapi/` | 53 |
| **Total** | **92** |

### 1.3 Correcciones aplicadas (triviales y de bajo riesgo)

Se corrigieron los hallazgos mecánicos, de bajo riesgo y sin impacto en el
comportamiento del sistema:

| Regla | Descripción | Instancias corregidas |
|---|---|---|
| `I001` | Orden/formato de bloque de imports | 8 archivos (`domain`, `backend-django`, `backend-fastapi`) |
| `UP037` | Comillas redundantes en anotación de tipo (`"Cantidad"` → `Cantidad`) | 1 (`domain/.../value_objects/cantidad.py`) |
| `UP041` | Alias innecesario de excepción (`socket.timeout` → `TimeoutError`) | 1 (`backend-fastapi/.../services/email_service.py`) |
| `F401` | Import no usado (`import socket`, dejado sin uso tras el fix anterior) | 1 (`backend-fastapi/.../services/email_service.py`) |

**Total corregido: 21 hallazgos.** Después de aplicar los fixes se corrió de
nuevo la suite completa de tests del dominio (`pytest`, 43 pruebas) para
confirmar que ningún cambio alteró comportamiento: **43 passed**. También se
verificó que `backend-fastapi/app/services/email_service.py` sigue
compilando (`python -m py_compile`) tras retirar el import huérfano.

Ninguna de estas correcciones tocó lógica de negocio, contratos de API, ni
las decisiones arquitectónicas del proyecto.

### 1.4 Resultado final (después de correcciones)

| Paquete | Hallazgos restantes |
|---|---|
| `domain/` | 15 |
| `backend-django/` | 12 |
| `backend-fastapi/` | 45 |
| **Total** | **72** |

### 1.5 Hallazgos restantes: documentados como deuda pendiente (no corregidos)

Se decidió no aplicar refactors grandes basados en estos hallazgos. Lo que
sigue **no se modificó** y queda documentado como deuda de bajo riesgo:

- **`E501` (línea > 88 caracteres): 53 instancias en total** (13 en
  `domain`, 12 en `backend-django`, 28 en `backend-fastapi`). Es un hallazgo
  puramente cosmético (longitud de línea), pero corregirlo de forma
  sistemática habría implicado tocar decenas de archivos en todo el
  repositorio para un beneficio marginal, aunque cada cambio individual sea
  trivial. Se deja como deuda de estilo de bajo riesgo.
- **`B008` en `backend-fastapi`: 17 instancias**
  (`Depends(...)` como valor por defecto de un parámetro, en `deps.py`,
  `api/ia.py`, `api/inventario.py`, `core/security.py`). Esto **no es un
  defecto real**: es el patrón idiomático y documentado de FastAPI para
  inyección de dependencias. Ruff lo marca porque la regla `B008` (de
  flake8-bugbear) fue diseñada de forma genérica para Python y no reconoce el
  patrón de FastAPI como una excepción. Se documenta como **falso positivo
  aceptado**, no como pendiente a corregir.
- **`N818`, 1 instancia** (`domain/.../exceptions.py`): la excepción
  `ErrorGeneracionEmbedding` no termina en `Error` según la convención
  `pep8-naming`. Renombrarla tocaría todos los `import`/`except` que la
  referencian en el dominio y en `backend-fastapi`; no es un cambio de una
  sola línea, así que se deja documentado como pendiente.
- **`B904`, 1 instancia** (`domain/.../value_objects/precio.py:37`): un
  `raise` dentro de un `except` sin encadenar (`raise ... from err`). Es de
  bajo riesgo, pero implica revisar el mensaje de error resultante para el
  consumidor de esa excepción (Django/FastAPI), así que se deja documentado
  en vez de tocar el comportamiento de una validación de dominio sin una
  revisión dedicada a la capa de dominio.

### 1.6 Conclusión de esta sección

El proyecto no presenta bugs reales de Pyflakes (ningún `F` restante salvo el
ya corregido), ni imports no usados restantes. Los 72 hallazgos que quedan
son, en su gran mayoría, estilo cosmético (`E501`) o un falso positivo propio
del patrón de FastAPI (`B008`); ninguno representa una falla funcional.

---

## 2. Análisis estático del frontend (ESLint)

### 2.1 Herramienta

El frontend ya contaba con **ESLint 9** configurado (`eslint-config-next`
16.2.10, perfiles `core-web-vitals` y `typescript`), como dependencia de
desarrollo (`devDependencies` en `package.json`), cumpliendo con el criterio
de no ser una dependencia de producción.

### 2.2 Resultado real

```bash
cd frontend
npm run lint
```

```
> frontend@0.1.0 lint
> eslint

(sin salida: 0 errores, 0 advertencias)
```

**0 hallazgos.** No se requirió ninguna corrección en el frontend.

---

## 3. Lighthouse (frontend en modo producción)

### 3.1 Build de producción: evidencia real

Se generó el build de producción real del frontend:

```bash
cd frontend
npm run build
```

Resultado (real, íntegro):

```
▲ Next.js 16.2.10 (Turbopack)
✓ Compiled successfully in 7.9s
  Running TypeScript ...
  Finished TypeScript in 6.2s ...
✓ Generating static pages using 1 worker (8/8) in 250ms

Route (app)
┌ ○ /
├ ○ /_not-found
├ ○ /empresas
├ ○ /inventario
├ ○ /login
└ ○ /productos

○  (Static)  prerendered as static content
```

Las 6 rutas de la aplicación (incluida `/_not-found`) se pre-renderizan como
contenido **estático** (`○`), lo cual es un indicador de rendimiento real y
verificable por sí mismo: no dependen de renderizado en servidor por
request, lo que favorece directamente las métricas que Lighthouse mide
(TTFB, FCP, LCP).

El servidor de producción (`npm run start`) se levantó y respondió
`HTTP 200` en `/` de forma real, confirmando que el build es funcional:

```bash
npm run start -- -p 3300
curl -o /dev/null -w "%{http_code}" http://localhost:3300/
# 200
```

Tamaño del bundle JS estático generado (`.next/static`, sin comprimir):
**772 KB** en total. Es un tamaño razonable para una aplicación de 4 vistas
sin librerías pesadas adicionales (no se usan librerías de gráficas, mapas, o
UI kits grandes en el frontend), coherente con el principio de simplicidad
del proyecto.

### 3.2 Ejecución de Lighthouse: resultado real sobre el despliegue en producción

El frontend se desplegó en Vercel
(`https://enterprise-inventory-platform-beige.vercel.app/`), lo que permitió
ejecutar Lighthouse contra una URL pública real en vez de un build local, vía
**PageSpeed Insights** (Google), que ejecuta Lighthouse internamente sobre
Chrome real.

**Móvil:**

| Categoría | Puntaje |
|---|---|
| Performance | 98 |
| Accessibility | 93 |
| Best Practices | 100 |
| SEO | 100 |

**Escritorio:**

| Categoría | Puntaje |
|---|---|
| Performance | 100 |
| Accessibility | 93 |
| Best Practices | 100 |
| SEO | 100 |

El único puntaje que no alcanza el máximo en ambos perfiles es
Accessibility (93/100), un resultado sólido (por encima del umbral de 90 que
Lighthouse considera aprobado) coherente con el cuidado ya presente en el
frontend en materia de accesibilidad: uso de `aria-describedby` y
`aria-invalid` dinámicos en `FormField` para enlazar errores y ayudas con
cada control, `aria-label` en botones de icono (mostrar/ocultar contraseña,
quitar precio), y semántica HTML nativa (`<label>`, `<button>`) en lugar de
elementos genéricos con manejadores de clic. El margen restante corresponde
a mejoras incrementales de detalle (por ejemplo, contraste de algún color
puntual) y no representa una falla estructural de accesibilidad.

### 3.3 Cómo reproducir este resultado

```
1. Desplegar el frontend (por ejemplo en Vercel).
2. Ir a https://pagespeed.web.dev/
3. Pegar la URL pública del despliegue.
4. Analizar en modo "Mobile" y en modo "Desktop" por separado.
```

---

## 4. GTmetrix

Al igual que Lighthouse, GTmetrix mide una URL servida realmente. Con el
despliegue del frontend en Vercel
(`https://enterprise-inventory-platform-beige.vercel.app/`) se ejecutó un
análisis real en <https://gtmetrix.com/>, con el siguiente resultado:

| Indicador | Resultado |
|---|---|
| GTmetrix Grade | **A** |
| Performance | 100% |
| Structure | 100% |
| LCP (Largest Contentful Paint) | 671 ms |
| TBT (Total Blocking Time) | 8 ms |
| CLS (Cumulative Layout Shift) | 0.01 |

Servidor de prueba: Seattle, WA, USA. Motor usado internamente por GTmetrix:
Chrome 142.0.0.0 con Lighthouse 12.6.1 (GTmetrix ejecuta Lighthouse como
parte de su propio análisis, además de sus métricas propias de Performance y
Structure).

---

## 5. Resumen ejecutivo

| Indicador | Estado | Evidencia |
|---|---|---|
| Análisis de calidad Python (equivalente SonarQube) | **Ejecutado, real** | Sección 1: 92 → 72 hallazgos, 21 corregidos, resto documentado |
| Análisis de calidad frontend (ESLint) | **Ejecutado, real** | Sección 2: 0 hallazgos |
| Build de producción del frontend | **Ejecutado, real** | Sección 3.1: build exitoso, 6/6 rutas estáticas, 772 KB |
| Lighthouse (vía PageSpeed Insights, sobre despliegue en Vercel) | **Ejecutado, real** | Sección 3.2: Móvil 98/93/100/100, Escritorio 100/93/100/100 (Performance/Accessibility/Best Practices/SEO) |
| GTmetrix (sobre despliegue en Vercel) | **Ejecutado, real** | Sección 4: Grade A, Performance 100%, Structure 100%, LCP 671 ms, TBT 8 ms, CLS 0.01 |

Ninguna herramienta de análisis (`ruff`, `eslint`) quedó como dependencia de
producción: `ruff` vive únicamente en `requirements-dev.txt` (raíz del
repo, fuera de los `requirements.txt` de Django/FastAPI); `eslint` ya vivía
en `devDependencies` del frontend.

URL pública usada para las mediciones de Lighthouse y GTmetrix:
`https://enterprise-inventory-platform-beige.vercel.app/`.
