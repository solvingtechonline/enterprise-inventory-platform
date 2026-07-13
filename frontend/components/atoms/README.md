# Atoms

Componentes indivisibles de la interfaz. No dependen de otros componentes
del proyecto, solo de los tokens definidos en `app/globals.css` y, cuando
aplica, de las props HTML nativas del elemento que envuelven.

- **`Button`**: botón con variantes `primario`, `secundario`, `peligro` y
  `texto`, y tamaños `sm`/`md`. Acepta `isLoading` para mostrar un spinner
  en lugar del contenido y deshabilitarse mientras dura una acción.
- **`Input`**, **`Select`**, **`TextArea`**: campos de formulario con la
  prop `invalid` para marcar error visualmente. Se combinan con `Label`,
  `ErrorText` y el molecule `FormField` para formar un campo accesible
  completo (label, control, texto de ayuda o error, `aria-describedby`).
- **`Label`**: etiqueta de campo, con indicador opcional de campo
  requerido.
- **`ErrorText`**: mensaje de error de un campo. No renderiza nada si no
  recibe texto.
- **`Badge`**: etiqueta corta de estado (`primario`, `neutro`, `exito`,
  `peligro`). Se usa para roles de usuario, códigos de producto/empresa y
  resultados de búsqueda semántica.
- **`Spinner`**: indicador de carga con texto accesible (`role="status"`).

## Convenciones

- Los átomos consumen colores, radios y sombras exclusivamente por nombre
  de token (`bg-primary`, `rounded-sm`, `shadow-xs`, etc.), nunca valores
  hexadecimales ni medidas sueltas. El valor real de cada token vive en
  `app/globals.css`.
- Ningún átomo importa otro átomo ni ningún molecule/organism. Si un
  componente necesita combinar dos átomos, ese componente pertenece a
  `molecules/` o a una capa superior, no a `atoms/`.
