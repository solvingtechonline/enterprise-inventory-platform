"use client";

import Link from "next/link";

import { Button } from "../atoms/Button";
import { useAuth } from "../../lib/auth/AuthContext";
import { EmptyState } from "../molecules/EmptyState";

/**
 * Envuelve vistas que requieren rol Administrador incluso para lectura
 * (Productos e Inventario). El backend es siempre la autoridad real;
 * este componente solo evita mostrar un formulario que de todos modos
 * sería rechazado.
 */
export function AuthGate({ children }: { children: React.ReactNode }) {
  const { isAdmin, isReady } = useAuth();

  if (!isReady) return null;

  if (!isAdmin) {
    return (
      <EmptyState
        title="Esta sección requiere rol Administrador"
        description="Inicia sesión con una cuenta de Administrador para consultar y gestionar este módulo."
        action={
          <Link href="/login">
            <Button variante="primario" tamano="sm">
              Iniciar sesión
            </Button>
          </Link>
        }
      />
    );
  }

  return <>{children}</>;
}
