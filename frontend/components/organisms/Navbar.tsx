"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { Button } from "../atoms/Button";
import { ConfirmDialog } from "../molecules/ConfirmDialog";
import { useAuth } from "../../lib/auth/AuthContext";

const enlaces = [
  { href: "/empresas", label: "Empresas" },
  { href: "/productos", label: "Productos" },
  { href: "/inventario", label: "Inventario" },
];

/*
 * Tono muted específico para texto secundario sobre el fondo oscuro del
 * navbar (subtítulo de marca, email de sesión). No es un token global del
 * sistema de diseño (--color-ink-muted ya está reservado para texto muted
 * sobre fondos claros): es una variante de contraste solo para este
 * componente, por eso se define como valor arbitrario local en vez de
 * agregarse a globals.css.
 */
const mutedSobreOscuro = "text-[#a8afc4]";

export function Navbar() {
  const { isAdmin, correo, logout, isReady } = useAuth();
  const pathname = usePathname();
  const router = useRouter();
  const [confirmandoLogout, setConfirmandoLogout] = useState(false);

  const confirmarLogout = () => {
    logout();
    setConfirmandoLogout(false);
    router.push("/");
  };

  return (
    <header className="bg-primary">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3 px-6 py-4">
        <Link href="/" className="flex flex-col leading-tight">
          <span className={`font-sans text-[10px] font-semibold tracking-widest ${mutedSobreOscuro}`}>
            Lite Thinking
          </span>
          <span className="font-display text-lg font-semibold text-primary-ink">
            Prueba Técnica
          </span>
        </Link>

        <nav className="flex items-center gap-1">
          {enlaces.map((enlace) => {
            const activo = pathname === enlace.href;
            return (
              <Link
                key={enlace.href}
                href={enlace.href}
                className={`rounded-full px-3 py-1.5 text-sm font-medium transition-colors ${
                  activo
                    ? "bg-accent text-accent-ink"
                    : `${mutedSobreOscuro} hover:text-white`
                }`}
              >
                {enlace.label}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-3">
          {isReady && isAdmin ? (
            <>
              <div className="flex items-center gap-2">
                <span className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary-soft text-primary">
                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth={1.75}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="h-4 w-4"
                    aria-hidden="true"
                  >
                    <circle cx="12" cy="8" r="4" />
                    <path d="M4 20c0-4 3.5-7 8-7s8 3 8 7" />
                  </svg>
                </span>
                <div className="leading-tight">
                  <p className="text-xs font-semibold uppercase tracking-wide text-primary-ink">
                    Administrador
                  </p>
                  {correo && <p className={`text-xs ${mutedSobreOscuro}`}>{correo}</p>}
                </div>
              </div>
              {/*
                La variante "secundario" de Button asume texto/borde oscuros
                para fondos claros (text-primary, border-border-strong), que
                sobre este navbar oscuro serían invisibles. Se sobreescriben
                solo esas clases con `!` (important) para no depender del
                orden de generación de Tailwind, sin tocar Button.tsx.
              */}
              <Button
                variante="secundario"
                tamano="sm"
                onClick={() => setConfirmandoLogout(true)}
                className="!border-white/30 !text-primary-ink hover:!border-white/60 hover:!bg-white/10"
              >
                Cerrar sesión
              </Button>
            </>
          ) : isReady ? (
            <>
              <div className="flex items-center gap-2">
                <span className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-white/25 text-white/70">
                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth={1.75}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="h-4 w-4"
                    aria-hidden="true"
                  >
                    <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                </span>
                <p className={`text-xs font-semibold uppercase tracking-wide ${mutedSobreOscuro}`}>
                  Visitante externo
                </p>
              </div>
              <Link href="/login">
                {/*
                  La variante "primario" de Button usa bg-primary: sobre un
                  navbar que ahora también es bg-primary, el botón se
                  camuflaría. Se usa el acento lima (mismo tono del enlace
                  activo) para que el CTA de login destaque, con outline de
                  foco oscuro en vez de acento (un anillo lima sobre botón
                  lima no se vería).
                */}
                <Button
                  variante="primario"
                  tamano="sm"
                  className="!bg-accent !text-accent-ink hover:!bg-accent-hover focus-visible:!outline-primary-ink"
                >
                  Iniciar sesión
                </Button>
              </Link>
            </>
          ) : null}
        </div>
      </div>

      {confirmandoLogout && (
        <ConfirmDialog
          title="Cerrar sesión"
          description="¿Seguro que quieres cerrar tu sesión?"
          confirmLabel="Cerrar sesión"
          onConfirm={confirmarLogout}
          onCancel={() => setConfirmandoLogout(false)}
        />
      )}
    </header>
  );
}
