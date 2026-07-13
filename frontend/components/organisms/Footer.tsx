function IconoEnlaceExterno() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-3 w-3"
      aria-hidden="true"
    >
      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
      <path d="M15 3h6v6" />
      <path d="M10 14 21 3" />
    </svg>
  );
}

/**
 * Pie de página global, montado una única vez en `app/layout.tsx` junto
 * al `Navbar`. Contenido estático, sin datos ni estado propio.
 */
export function Footer() {
  return (
    <footer className="border-t border-border bg-surface">
      <div className="mx-auto max-w-5xl px-6 py-4 text-center">
        <p className="text-xs text-ink-muted">
          Prueba técnica desarrollada por{" "}
          <a
            href="https://linkedin.com/in/samuel-toro-a32b9829b"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-ink underline underline-offset-2
              transition-colors hover:text-primary
              focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            Samuel Toro
            <IconoEnlaceExterno />
          </a>
          {" · "}
          <a
            href="https://samueltoro.site"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-ink underline underline-offset-2
              transition-colors hover:text-primary
              focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            samueltoro.site
            <IconoEnlaceExterno />
          </a>
        </p>
      </div>
    </footer>
  );
}
