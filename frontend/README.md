# Frontend de Lite Thinking 2026

Next.js 16 (App Router) + React 19, consumiendo la API de Django
(Empresa, Productos, Login) y la API de FastAPI (Inventario, PDF, correo,
agente de IA). El detalle de arquitectura completa del proyecto está en
el `README.md` de la raíz del repositorio; este documento cubre solo el
frontend.

## Requisitos

- Node.js 20 LTS (requerido por Next.js 16).
- Los backends de Django y FastAPI corriendo, o al menos accesibles en
  las URLs configuradas (ver más abajo).

## Instalación y ejecución

```bash
npm install
npm run dev
```

Esto levanta el servidor de desarrollo en `http://localhost:3000`.

Otros scripts disponibles:

| Script | Qué hace |
|---|---|
| `npm run dev` | Servidor de desarrollo con recarga en caliente. |
| `npm run build` | Build de producción. Requiere salida de red hacia `fonts.googleapis.com` para descargar Sora e Inter vía `next/font/google`. |
| `npm run start` | Sirve el build de producción ya generado. |
| `npm run lint` | ESLint sobre todo el proyecto. |

### Variables de entorno (`frontend/.env.local`)

| Variable | Descripción |
|---|---|
| `NEXT_PUBLIC_DJANGO_API_URL` | URL base de la API de Django (por defecto `http://localhost:8000/api`). |
| `NEXT_PUBLIC_FASTAPI_API_URL` | URL base de la API de FastAPI (por defecto `http://localhost:8001`). |

## Estructura: Atomic Design

Los componentes de React están organizados en cuatro capas, cada una con
su propio `README.md`:

- **`components/atoms/`**: componentes indivisibles (`Button`, `Input`,
  `Select`, `TextArea`, `Label`, `ErrorText`, `Badge`, `Spinner`). No
  dependen de otros componentes del proyecto.
- **`components/molecules/`**: combinaciones simples de átomos
  (`FormField`, `Alert`, `Modal`, `ConfirmDialog`, `EmptyState`,
  `PrecioRow`).
- **`components/organisms/`**: bloques funcionales completos por vista
  (`Navbar`, `Footer`, `LoginForm`, las tablas y los `FormModal` de
  Empresa, Producto e Inventario, `EnviarCorreoModal`,
  `BusquedaSemanticaProductos`).
- **`components/templates/`**: estructura de página sin datos reales
  (`PageShell`, `AuthGate`). Las rutas en `app/` las instancian con datos.

Cada capa solo puede depender de las capas anteriores en esta lista
(`organisms` puede usar `molecules` y `atoms`, pero no al revés).

### Rutas (`app/`)

`/` (inicio), `/login`, `/empresas`, `/productos`, `/inventario`. Cada
carpeta de ruta tiene su propio `README.md` describiendo el propósito de
esa vista.

### `lib/`

- `lib/api/`: clientes REST hacia Django y FastAPI.
- `lib/auth/`: `AuthContext` y decodificación del JWT.
- `lib/types/`: tipos TypeScript compartidos entre componentes.
- `lib/utils/`: utilidades varias (descarga de archivos PDF).

## Sistema de diseño

Los tokens visuales viven en `app/globals.css`, dentro de `:root` y del
bloque `@theme inline` de Tailwind v4 (que convierte cada variable CSS en
una clase utilitaria: `--color-primary` genera `bg-primary`,
`text-primary`, `border-primary`, etc.). Ningún componente debe usar un
valor hexadecimal, un radio o una sombra sueltos: siempre por nombre de
token.

### Color

- **Neutros**: `bg`, `surface`, `surface-muted`, `surface-sunken`,
  `border`, `border-strong`, `ink`, `ink-muted`. Forman la base tonal de
  fondos, superficies y texto.
- **`primary`** (+ `primary-hover`, `primary-ink`, `primary-soft`): color
  de marca, usado en botones principales, enlaces activos y el fondo del
  `Navbar`.
- **`accent`** (+ `accent-hover`, `accent-ink`, `accent-soft`): color de
  alto contraste reservado para estados activos y el anillo de foco por
  teclado (`focus-visible`) en toda la interfaz.
- **`danger`** (+ variantes) y **`success`** (+ variante `soft`): estados
  de error/eliminación y de éxito respectivamente.

### Radio y sombra

Escala de tres pasos para ambos: `sm` / `md` / `lg`. Como guía general,
`sm` es para controles compactos (botones, inputs), `md` para paneles
anidados o secundarios, y `lg` para contenedores de primer nivel
(tarjetas, tablas, modales).

### Tipografía

- **`font-display`** (Sora): títulos y encabezados. Solo están cargados
  los pesos 600 y 700, así que todo uso de `font-display` debe ir
  acompañado explícitamente de `font-semibold` o `font-bold`; sin eso, el
  navegador cae al tipo de letra de respaldo en vez de mostrar Sora.
- **`font-sans`** (Inter): texto de cuerpo, el valor por defecto de toda
  la aplicación.
- **`font-mono`**: códigos de producto, NIT, cifras y precios.

## Notas de compatibilidad

- `next/font/google` descarga los archivos de fuente durante el build.
  En entornos sin salida de red hacia `fonts.googleapis.com`, `npm run
  build` falla específicamente en ese paso; el resto del proyecto no se
  ve afectado.
