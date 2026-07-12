"use client";

import { useEffect, useRef } from "react";

import { Label } from "../atoms/Label";
import { ErrorText } from "../atoms/ErrorText";

interface Props {
  htmlFor: string;
  label: string;
  required?: boolean;
  error?: string;
  hint?: string;
  children: React.ReactNode;
}

export function FormField({ htmlFor, label, required, error, hint, children }: Props) {
  const contenedorRef = useRef<HTMLDivElement>(null);
  const hintId = `${htmlFor}-hint`;
  const errorId = `${htmlFor}-error`;

  // Enlaza el hint/error con el o los controles reales dentro de children
  // (input, select, textarea) vía aria-describedby. Se hace por DOM en vez
  // de cloneElement porque children no siempre es un único control directo:
  // por ejemplo, el campo de contraseña envuelve el Input junto al botón de
  // mostrar/ocultar en un <div> local (ver LoginForm), y el campo de
  // Precios en ProductoFormModal renderiza varias filas de inputs dentro de
  // un mismo FormField. Buscar todos los controles cubre ambos casos sin
  // que cada consumidor tenga que resolverlo por su cuenta.
  useEffect(() => {
    const contenedor = contenedorRef.current;
    if (!contenedor) return;

    const ids = [hint && !error ? hintId : null, error ? errorId : null]
      .filter(Boolean)
      .join(" ");

    const controles = contenedor.querySelectorAll<HTMLElement>("input, select, textarea");
    controles.forEach((control) => {
      if (ids) {
        control.setAttribute("aria-describedby", ids);
      } else {
        control.removeAttribute("aria-describedby");
      }
      if (error) {
        control.setAttribute("aria-invalid", "true");
      } else {
        control.removeAttribute("aria-invalid");
      }
    });
  }, [hint, error, hintId, errorId]);

  return (
    <div>
      <Label htmlFor={htmlFor} required={required}>
        {label}
      </Label>
      <div className="mt-1" ref={contenedorRef}>
        {children}
      </div>
      {hint && !error && (
        <p id={hintId} className="mt-1 text-xs text-ink-muted">
          {hint}
        </p>
      )}
      <ErrorText id={errorId}>{error}</ErrorText>
    </div>
  );
}
