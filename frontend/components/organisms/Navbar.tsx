"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { Badge } from "../atoms/Badge";
import { Button } from "../atoms/Button";
import { useAuth } from "../../lib/auth/AuthContext";

const enlaces = [
  { href: "/empresas", label: "Empresas" },
  { href: "/productos", label: "Productos" },
  { href: "/inventario", label: "Inventario" },
];

export function Navbar() {
  const { isAdmin, correo, logout, isReady } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  return (
    <header className="border-b border-border bg-surface">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3 px-6 py-4">
        <Link href="/" className="flex items-baseline gap-2">
          <span className="font-display text-lg font-semibold text-primary">Lite Thinking</span>
          <span className="font-mono text-xs uppercase tracking-widest text-ink-muted">
            libro mayor
          </span>
        </Link>

        <nav className="flex items-center gap-1">
          {enlaces.map((enlace) => {
            const activo = pathname === enlace.href;
            return (
              <Link
                key={enlace.href}
                href={enlace.href}
                className={`rounded-sm px-3 py-1.5 text-sm font-medium transition-colors ${
                  activo
                    ? "bg-primary-soft text-primary"
                    : "text-ink-muted hover:bg-surface-muted hover:text-ink"
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
              <div className="text-right leading-tight">
                <Badge tono="primario">administrador</Badge>
                {correo && <p className="mt-0.5 text-xs text-ink-muted">{correo}</p>}
              </div>
              <Button variante="secundario" tamano="sm" onClick={handleLogout}>
                Cerrar sesión
              </Button>
            </>
          ) : isReady ? (
            <>
              <Badge tono="neutro">visitante externo</Badge>
              <Link href="/login">
                <Button variante="primario" tamano="sm">
                  Iniciar sesión
                </Button>
              </Link>
            </>
          ) : null}
        </div>
      </div>
    </header>
  );
}
