"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Badge } from "../components/atoms/Badge";
import { PageShell } from "../components/templates/PageShell";
import { useAuth } from "../lib/auth/AuthContext";
import { listarEmpresas } from "../lib/api/empresas";

interface Acceso {
  href: string;
  titulo: string;
  descripcion: string;
  disponible: boolean;
}

/*
 * Ícono representativo por tarjeta, mapeado por href en vez de agregarse
 * al array `accesos` para no tocar su forma de datos ni la lógica de
 * `disponible`. SVG inline, sin librería externa.
 */
const iconosPorHref: Record<string, React.ReactNode> = {
  "/empresas": (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-5 w-5"
      aria-hidden="true"
    >
      <path d="M4 21V5a1 1 0 0 1 1-1h8a1 1 0 0 1 1 1v16" />
      <path d="M14 10h5a1 1 0 0 1 1 1v10" />
      <path d="M4 21h16" />
      <path d="M8 8h1M11 8h1M8 12h1M11 12h1M8 16h1M11 16h1" />
    </svg>
  ),
  "/productos": (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-5 w-5"
      aria-hidden="true"
    >
      <path d="M21 8 12 3 3 8v8l9 5 9-5Z" />
      <path d="M3 8l9 5 9-5" />
      <path d="M12 13v8" />
    </svg>
  ),
  "/inventario": (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-5 w-5"
      aria-hidden="true"
    >
      <path d="M3 10 12 4l9 6" />
      <path d="M4 10v10h16V10" />
      <path d="M9 20v-6h6v6" />
    </svg>
  ),
};

export default function Home() {
  const { isAdmin, isReady } = useAuth();
  const [totalEmpresas, setTotalEmpresas] = useState<number | null>(null);

  useEffect(() => {
    listarEmpresas()
      .then((datos) => setTotalEmpresas(datos.length))
      .catch(() => setTotalEmpresas(null));
  }, []);

  const accesos: Acceso[] = [
    {
      href: "/empresas",
      titulo: "Empresas",
      descripcion: "Consulta el directorio de empresas. Lectura abierta para cualquier visitante.",
      disponible: true,
    },
    {
      href: "/productos",
      titulo: "Productos",
      descripcion: "Administra el catálogo de productos y sus precios por moneda.",
      disponible: isReady && isAdmin,
    },
    {
      href: "/inventario",
      titulo: "Inventario",
      descripcion: "Registra y consulta existencias de productos por empresa.",
      disponible: isReady && isAdmin,
    },
  ];

  return (
    <PageShell
      title="Gestión de Empresas, Productos e Inventario"
      description={
        totalEmpresas !== null
          ? `${totalEmpresas} ${totalEmpresas === 1 ? "empresa registrada" : "empresas registradas"} en el sistema.`
          : undefined
      }
    >
      <div className="grid gap-4 sm:grid-cols-3">
        {accesos.map((acceso) => (
          <Link
            key={acceso.href}
            href={acceso.disponible ? acceso.href : "/login"}
            className="group rounded-lg border border-border bg-surface p-5 shadow-xs
              transition-all hover:-translate-y-0.5 hover:border-border-strong hover:shadow-md"
          >
            <div className="mb-3 flex items-center justify-between">
              <span className="inline-flex h-10 w-10 items-center justify-center rounded-md bg-primary-soft text-primary">
                {iconosPorHref[acceso.href]}
              </span>
              {!acceso.disponible && <Badge tono="neutro">requiere login</Badge>}
            </div>
            <h2 className="font-display text-lg font-semibold text-ink">{acceso.titulo}</h2>
            <p className="mt-1 text-sm text-ink-muted">{acceso.descripcion}</p>
          </Link>
        ))}
      </div>
    </PageShell>
  );
}
