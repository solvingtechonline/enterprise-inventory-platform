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
            className="group rounded-md border border-border bg-surface p-5 transition-shadow hover:shadow-md"
          >
            <div className="mb-3 flex items-center justify-between">
              <h2 className="font-display text-lg text-ink">{acceso.titulo}</h2>
              {!acceso.disponible && <Badge tono="neutro">requiere login</Badge>}
            </div>
            <p className="text-sm text-ink-muted">{acceso.descripcion}</p>
          </Link>
        ))}
      </div>
    </PageShell>
  );
}
